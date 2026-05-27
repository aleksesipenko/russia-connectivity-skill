#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


DEFAULT_TIMEZONE = "Europe/Moscow"
DEFAULT_ANALYZER = Path(__file__).resolve().with_name("analyze_telegram_intel.py")


@dataclass(frozen=True)
class ChatSpec:
    slug: str
    sender: str
    max_messages: int


CHATS = (
    ChatSpec("vpn-protocols", "Обсуждение VPN-протоколов", 12000),
    ChatSpec("itdog-chat", "ITDog Chat", 20000),
)


def format_local(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def run_export(
    exporter: Path,
    chat: ChatSpec,
    from_local: str,
    to_local: str,
    timezone_name: str,
    out_dir: Path,
) -> Path:
    cmd = [
        "python3",
        str(exporter),
        "--sender",
        chat.sender,
        "--from-local",
        from_local,
        "--to-local",
        to_local,
        "--timezone",
        timezone_name,
        "--include-pinned",
        "--no-download-media",
        "--no-transcribe",
        "--max-messages",
        str(chat.max_messages),
        "--max-pinned",
        "200",
        "--out-dir",
        str(out_dir),
    ]
    subprocess.run(cmd, check=True, timeout=1800)
    return out_dir / "corrections-package.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh private Telegram VPN intelligence packages and summary")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--base-dir", default="~/.local/russia-connectivity/telegram-intel")
    parser.add_argument(
        "--exporter",
        default=os.environ.get("RUSSIA_CONNECTIVITY_TELEGRAM_EXPORTER"),
        help="Path to a compatible Telegram export script, or set RUSSIA_CONNECTIVITY_TELEGRAM_EXPORTER.",
    )
    parser.add_argument("--analyzer", default=str(DEFAULT_ANALYZER))
    parser.add_argument("--skip-analyze", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tz = ZoneInfo(args.timezone)
    now_local = datetime.now(tz)
    since_local = now_local - timedelta(days=args.days)

    base_dir = Path(args.base_dir).expanduser()
    run_dir = base_dir / now_local.strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    if not args.exporter:
        raise SystemExit(
            "Missing Telegram exporter. Pass --exporter /path/to/exporter.py "
            "or set RUSSIA_CONNECTIVITY_TELEGRAM_EXPORTER."
        )

    exporter = Path(args.exporter).expanduser()
    analyzer = Path(args.analyzer).expanduser()

    from_local = format_local(since_local)
    to_local = format_local(now_local)

    manifest: dict[str, object] = {
        "generated_at_local": now_local.isoformat(),
        "timezone": args.timezone,
        "days": args.days,
        "from_local": from_local,
        "to_local": to_local,
        "run_dir": str(run_dir),
        "packages": {},
    }

    package_paths: dict[str, Path] = {}
    for chat in CHATS:
        out_dir = run_dir / chat.slug
        package_path = run_export(exporter, chat, from_local, to_local, args.timezone, out_dir)
        package_paths[chat.slug] = package_path
        manifest["packages"][chat.slug] = {
            "sender": chat.sender,
            "package_json": str(package_path),
            "index_md": str(out_dir / "INDEX.md"),
            "messages_jsonl": str(out_dir / "messages.jsonl"),
        }

    summary_md = run_dir / "telegram-intel-summary.md"
    summary_json = run_dir / "telegram-intel-summary.json"
    if not args.skip_analyze:
        subprocess.run(
            [
                "python3",
                str(analyzer),
                "--vpn-package",
                str(package_paths["vpn-protocols"]),
                "--itdog-package",
                str(package_paths["itdog-chat"]),
                "--output-md",
                str(summary_md),
                "--output-json",
                str(summary_json),
            ],
            check=True,
            timeout=300,
        )
        manifest["summary_md"] = str(summary_md)
        manifest["summary_json"] = str(summary_json)

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"REFRESH_OK run_dir={run_dir} manifest={manifest_path}")
    if not args.skip_analyze:
        print(f"SUMMARY_MD={summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
