#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from intel_patterns import FAILURE_MODES


DEFAULT_TIMEZONE = "Europe/Moscow"
DEFAULT_OUTPUT_DIR = "~/.local/russia-connectivity/telegram-intel"
DEFAULT_TELEGRAM_MCP_COMMAND = "telegram-mcp"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh Telegram field intelligence through telegram-mcp.")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--base-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--command", default=DEFAULT_TELEGRAM_MCP_COMMAND)
    parser.add_argument(
        "--chat",
        action="append",
        default=[],
        help="Chat title, username, or id. Repeat for multiple chats.",
    )
    parser.add_argument("--max-messages", type=int, default=500)
    return parser.parse_args()


def parse_message_date(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None
    return None


def message_text(message: dict[str, Any]) -> str:
    for key in ("text", "message", "effective_text", "caption"):
        value = message.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def classify_text(text: str) -> list[str]:
    folded = text.casefold()
    labels = []
    for mode in FAILURE_MODES:
        if any(keyword.casefold() in folded for keyword in mode.keywords):
            labels.append(mode.key)
    return labels


def content_to_json(content: Any) -> Any:
    if isinstance(content, list) and content:
        text = getattr(content[0], "text", None)
        if isinstance(text, str):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
    return content


async def call_tool(session: ClientSession, tool_name: str, arguments: dict[str, Any]) -> Any:
    result = await session.call_tool(tool_name, arguments)
    return content_to_json(result.content)


async def resolve_chat_id(session: ClientSession, chat: str) -> int | str:
    if chat.lstrip("-").isdigit() or chat.startswith("@"):
        return chat

    wanted = chat.casefold()
    for page in range(1, 21):
        payload = await call_tool(session, "get_chats", {"page": page, "page_size": 100})
        rows = payload.get("results", []) if isinstance(payload, dict) else []
        if not rows:
            break
        for row in rows:
            title = str(row.get("title") or row.get("name") or "").casefold()
            if title == wanted:
                return row["chat_id"]
    return chat


async def refresh(args: argparse.Namespace) -> dict[str, Any]:
    chats = args.chat or ["ITDog Chat", "Обсуждение VPN-протоколов"]
    tz = ZoneInfo(args.timezone)
    now = datetime.now(tz)
    since = now - timedelta(days=args.days)
    run_dir = Path(args.base_dir).expanduser() / now.strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    server = StdioServerParameters(command=args.command, args=[])
    summary: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "since": since.isoformat(),
        "timezone": args.timezone,
        "chats": {},
        "symptom_counts": {},
        "run_dir": str(run_dir),
    }
    symptom_counts: Counter[str] = Counter()
    fresh_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for chat in chats:
                chat_id = await resolve_chat_id(session, chat)
                payload = await call_tool(
                    session,
                    "list_messages",
                    {
                        "chat_id": chat_id,
                        "limit": args.max_messages,
                    },
                )
                messages = payload.get("results", payload) if isinstance(payload, dict) else payload
                if not isinstance(messages, list):
                    messages = []

                selected = []
                for message in messages:
                    if not isinstance(message, dict):
                        continue
                    date = parse_message_date(message.get("date") or message.get("date_local"))
                    if date and date.tzinfo is not None:
                        date = date.astimezone(tz)
                    if date and date < since:
                        continue
                    text = message_text(message)
                    labels = classify_text(text)
                    for label in labels:
                        symptom_counts[label] += 1
                        if len(fresh_examples[label]) < 5:
                            fresh_examples[label].append(
                                {
                                    "chat": chat,
                                    "date": date.isoformat() if date else None,
                                    "text": text[:300],
                                }
                            )
                    selected.append(
                        {
                            "id": message.get("id"),
                            "date": date.isoformat() if date else message.get("date") or message.get("date_local"),
                            "text": text,
                            "labels": labels,
                        }
                    )

                chat_slug = "".join(ch if ch.isalnum() else "-" for ch in chat.casefold()).strip("-")
                out_path = run_dir / f"{chat_slug or 'chat'}.json"
                out_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                summary["chats"][chat] = {
                    "chat_id": chat_id,
                    "messages": len(selected),
                    "path": str(out_path),
                }

    summary["symptom_counts"] = dict(symptom_counts)
    summary["fresh_examples"] = fresh_examples
    summary_path = run_dir / "telegram-mcp-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary["summary_path"] = str(summary_path)
    return summary


def main() -> int:
    summary = asyncio.run(refresh(parse_args()))
    print(f"TELEGRAM_MCP_REFRESH_OK summary={summary['summary_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
