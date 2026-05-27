# Russia Connectivity Skill

A Codex skill for diagnosing and designing connectivity paths for Russia-based users when normal foreign infrastructure access cannot be assumed.

The skill focuses on failure classification before protocol choice: DNS or NSDI tampering, DPI behavior, port-specific filtering, ASN or hoster issues, routing policy, and runtime contract checks.

## Contents

- `SKILL.md` - main invocation rules and decision flow.
- `references/` - source lists, diagnostic matrix, protocol matrix, routing guidance, deployment paths, runbooks, and runtime contracts.
- `scripts/triage_case.py` - structured first-pass diagnosis from a JSON case file.
- `scripts/check_sources.py` - lightweight freshness check for curated public sources.
- `scripts/analyze_telegram_intel.py` - optional analyzer for compatible Telegram export packages.
- `scripts/refresh_telegram_intel.py` - optional wrapper for a user-provided Telegram exporter.
- `scripts/telegram_mcp_refresh.py` - optional refresh path through `chigwell/telegram-mcp`.
- `tests/` - focused unit tests for the local helper scripts.

## Install

Clone or copy this directory into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/aleksesipenko/russia-connectivity-skill.git ~/.codex/skills/russia-connectivity
```

Restart Codex after installing a new skill.

## Quick Checks

```bash
python3 tests/test_triage_case.py
python3 tests/test_analyze_telegram_intel.py
python3 scripts/check_sources.py
```

## Triage Example

```json
{
  "provider_type": "home",
  "scope": "router",
  "symptoms": ["dns", "domain disappears on russian resolvers"],
  "needs": ["whole-network coverage"]
}
```

Run:

```bash
python3 scripts/triage_case.py --input case.json --output report.json
```

## Private Telegram Intel

Telegram analysis is optional. The repository does not include credentials or sessions.

Preferred path: install `chigwell/telegram-mcp` from GitHub and configure it in read-only mode. Do not install the unrelated PyPI package named `telegram-mcp`.

```bash
python -m venv .venv-mcp
. .venv-mcp/bin/activate
pip install -r requirements-mcp.txt
```

Then configure your MCP client to run the installed `telegram-mcp` command with `TELEGRAM_EXPOSED_TOOLS=read-only`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and either `TELEGRAM_SESSION_STRING` or `TELEGRAM_SESSION_NAME`.

To generate a repeatable local field-intel artifact through MCP:

```bash
python3 scripts/telegram_mcp_refresh.py --days 7 --command /path/to/telegram-mcp
```

Fallback path: if you have a compatible exporter instead of MCP, pass it explicitly:

```bash
python3 scripts/refresh_telegram_intel.py --days 7 --exporter /path/to/telegram_exporter.py
```

Private field data should be used as an operational signal, then checked against public docs and empirical sources.
