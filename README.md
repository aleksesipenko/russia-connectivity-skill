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

Telegram analysis is optional. The repository does not include credentials, sessions, or a Telegram exporter. If you have a compatible exporter, pass it explicitly:

```bash
python3 scripts/refresh_telegram_intel.py --days 7 --exporter /path/to/telegram_exporter.py
```

Private field data should be used as an operational signal, then checked against public docs and empirical sources.
