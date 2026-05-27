#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from intel_patterns import FAILURE_MODES, normalize


@dataclass(frozen=True)
class Topic:
    name: str
    preferred_chat: str
    keywords: tuple[str, ...]


TOPICS = (
    Topic(
        name="edge-router-dns",
        preferred_chat="ITDog Chat",
        keywords=("podkop", "подкоп", "zapret", "dns", "днс", "openwrt", "роутер", "fakeip"),
    ),
    Topic(
        name="awg-openwrt",
        preferred_chat="ITDog Chat",
        keywords=("amnezia", "amneziawg", "awg", "wireguard", "xkeen"),
    ),
    Topic(
        name="server-443-reality-xhttp",
        preferred_chat="Обсуждение VPN-протоколов",
        keywords=("443", "xhttp", "reality", "selfsteal", "servernames", "nginx stream", "vision", "flow"),
    ),
    Topic(
        name="hosters-cloudflare-asn",
        preferred_chat="Обсуждение VPN-протоколов",
        keywords=("cloudflare", "warp", "cdn", "asn", "подсети", "host", "vps", "whitelist", "блеклист"),
    ),
    Topic(
        name="panels-and-deploy",
        preferred_chat="Обсуждение VPN-протоколов",
        keywords=("remnawave", "marzban", "3x-ui", "reverse proxy", "template", "subscription"),
    ),
    Topic(
        name="dpi-symptoms",
        preferred_chat="ITDog Chat",
        keywords=("dpi", "тспу", "ркн", "отвал", "блок", "не работает", "только через vpn", "handshake"),
    ),
)

ROLE_HINTS = {
    "ITDog Chat": "radar + router playbook",
    "Обсуждение VPN-протоколов": "server and protocol playbook",
}


DATE_FORMAT = "%Y-%m-%d %H:%M"


def load_package(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def text_for(message: dict) -> str:
    return str(message.get("effective_text") or message.get("text") or "")


def normalize(text: str) -> str:
    return text.casefold()


def topic_matches(message: dict, topic: Topic) -> bool:
    text = normalize(text_for(message))
    return any(keyword.casefold() in text for keyword in topic.keywords)


def select_rows(data: dict, topic: Topic, limit: int = 3) -> list[dict]:
    rows: list[dict] = []
    for message in reversed(data["messages"]):
        if topic_matches(message, topic):
            rows.append(message)
            if len(rows) >= limit:
                break
    return rows


def parse_local_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        pass
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Unsupported date format: {value}") from exc


def mode_matches(message: dict, keywords: tuple[str, ...]) -> bool:
    text = normalize(text_for(message))
    return any(keyword.casefold() in text for keyword in keywords)


def build_symptom_counts(packages: list[dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for mode in FAILURE_MODES:
        counts[mode.key] = {}
        for package in packages:
            counts[mode.key][package["dialog"]["name"]] = sum(
                1 for message in package["messages"] if mode_matches(message, mode.keywords)
            )
    return counts


def collect_fresh_examples(packages: list[dict], limit: int = 2) -> dict[str, list[dict]]:
    examples: dict[str, list[dict]] = {}
    for mode in FAILURE_MODES:
        rows: list[dict] = []
        for package in packages:
            for message in package["messages"]:
                if not mode_matches(message, mode.keywords):
                    continue
                rows.append(
                    {
                        "chat": package["dialog"]["name"],
                        "id": message["id"],
                        "date_local": message["date_local"],
                        "preview": " ".join(text_for(message).split())[:180],
                    }
                )
        rows.sort(key=lambda row: parse_local_date(row["date_local"]), reverse=True)
        examples[mode.key] = rows[:limit]
    return examples


def freshness_summary(package: dict, now: datetime) -> dict[str, object]:
    parsed = [parse_local_date(message["date_local"]) for message in package["messages"]]
    if not parsed:
        return {
            "latest_message_local": None,
            "messages_last_24h": 0,
            "messages_last_72h": 0,
        }

    latest = max(parsed)
    return {
        "latest_message_local": latest.strftime(DATE_FORMAT),
        "messages_last_24h": sum(1 for item in parsed if (now - item).total_seconds() <= 24 * 3600),
        "messages_last_72h": sum(1 for item in parsed if (now - item).total_seconds() <= 72 * 3600),
    }


def build_summary(packages: list[dict]) -> tuple[str, dict]:
    packages_by_name = {package["dialog"]["name"]: package for package in packages}
    topic_counts: dict[str, dict[str, int]] = {}
    for topic in TOPICS:
        topic_counts[topic.name] = {}
        for package in packages:
            count = sum(1 for message in package["messages"] if topic_matches(message, topic))
            topic_counts[topic.name][package["dialog"]["name"]] = count
    symptom_counts = build_symptom_counts(packages)
    fresh_examples = collect_fresh_examples(packages)
    all_dates = [
        parse_local_date(message["date_local"])
        for package in packages
        for message in package["messages"]
    ]
    now = max(all_dates) if all_dates else datetime.now()
    freshness = {
        package["dialog"]["name"]: freshness_summary(package, now)
        for package in packages
    }

    lines: list[str] = []
    lines.append("# Telegram Intel Summary")
    lines.append("")
    lines.append("## Role Split")
    lines.append("")
    for name, role in ROLE_HINTS.items():
        package = packages_by_name.get(name)
        if not package:
            continue
        lines.append(
            f"- `{name}`: {role}; `messages_in_window={package['counts']['messages_in_window']}`, "
            f"`pinned={package['counts']['pinned_messages']}`"
        )
    lines.append("")

    lines.append("## Freshness")
    lines.append("")
    for name, stats in freshness.items():
        lines.append(
            f"- `{name}`: latest=`{stats['latest_message_local']}`, "
            f"`last_24h={stats['messages_last_24h']}`, `last_72h={stats['messages_last_72h']}`"
        )
    lines.append("")

    lines.append("## Topic Heatmap")
    lines.append("")
    for topic in TOPICS:
        counts = topic_counts[topic.name]
        heat = ", ".join(f"{chat}={counts.get(chat, 0)}" for chat in packages_by_name)
        lines.append(f"- `{topic.name}` (start with `{topic.preferred_chat}`): {heat}")
    lines.append("")

    lines.append("## Symptom Heatmap")
    lines.append("")
    for mode in FAILURE_MODES:
        counts = symptom_counts[mode.key]
        heat = ", ".join(f"{chat}={counts.get(chat, 0)}" for chat in packages_by_name)
        lines.append(f"- `{mode.key}` (start with `{mode.preferred_chat}`): {heat}")
    lines.append("")

    lines.append("## Search Routes")
    lines.append("")
    lines.append("- Router, `OpenWrt`, `Podkop`, `zapret`, `DNS`, `AWG`: start with `ITDog Chat`.")
    lines.append("- `443`, `XHTTP`, `REALITY`, `SelfSteal`, panels, hosters, Cloudflare/CDN, server routing: start with `Обсуждение VPN-протоколов`.")
    lines.append("- If the symptom is ambiguous, search by symptom first, then by stack name.")
    lines.append("")

    lines.append("## Fresh Symptom Examples")
    lines.append("")
    for mode in FAILURE_MODES:
        lines.append(f"### {mode.key}")
        lines.append("")
        if not fresh_examples[mode.key]:
            lines.append("- No recent examples in this export window.")
            lines.append("")
            continue
        for row in fresh_examples[mode.key]:
            lines.append(f"- `{row['chat']}` `#{row['id']}` — {row['date_local']} — {row['preview']}")
        lines.append("")

    lines.append("## Current Topic Examples")
    lines.append("")
    for topic in TOPICS:
        lines.append(f"### {topic.name}")
        lines.append("")
        lines.append(f"Preferred chat: `{topic.preferred_chat}`")
        lines.append("")
        for chat_name, package in packages_by_name.items():
            rows = select_rows(package, topic, limit=2)
            if not rows:
                continue
            lines.append(f"- `{chat_name}`")
            for row in rows:
                preview = " ".join(text_for(row).split())[:180]
                lines.append(f"  - `{row['id']}` — {row['date_local']} — {preview}")
        lines.append("")

    lines.append("## Pinned First")
    lines.append("")
    for package in packages:
        lines.append(f"### {package['dialog']['name']}")
        for message in package["messages"]:
            if "pinned" not in message.get("export_tags", []):
                continue
            preview = " ".join(text_for(message).split())[:160]
            lines.append(f"- `{message['id']}` — {message['date_local']} — {preview}")
        lines.append("")

    machine_summary = {
        "role_split": ROLE_HINTS,
        "freshness": freshness,
        "topic_counts": topic_counts,
        "symptom_counts": symptom_counts,
        "fresh_examples": fresh_examples,
        "packages": {
            package["dialog"]["name"]: {
                "messages_in_window": package["counts"]["messages_in_window"],
                "pinned_messages": package["counts"]["pinned_messages"],
            }
            for package in packages
        },
    }
    return "\n".join(lines).rstrip() + "\n", machine_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize the private Telegram VPN intelligence layer")
    parser.add_argument("--vpn-package", required=True)
    parser.add_argument("--itdog-package", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packages = [
        load_package(Path(args.vpn_package).expanduser()),
        load_package(Path(args.itdog_package).expanduser()),
    ]
    summary_text, summary_json = build_summary(packages)
    Path(args.output_md).expanduser().write_text(summary_text, encoding="utf-8")
    Path(args.output_json).expanduser().write_text(
        json.dumps(summary_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ANALYZE_OK md={args.output_md} json={args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
