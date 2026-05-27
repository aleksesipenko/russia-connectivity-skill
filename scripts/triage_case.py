#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from intel_patterns import dominant_mode, score_failure_modes


def unknown_fields(case: dict) -> list[str]:
    missing: list[str] = []
    for field in ("region", "provider_name", "provider_type", "scope"):
        value = case.get(field)
        if not value:
            missing.append(field)

    scope = str(case.get("scope") or "").casefold()
    if "router" in scope:
        if not case.get("router_model"):
            missing.append("router_model")
    elif scope in {"single-device", "single device", "desktop", "laptop"}:
        if not case.get("client_os"):
            missing.append("client_os")

    if not case.get("symptoms"):
        missing.append("symptoms")
    return missing


def derive_assumptions(case: dict, missing: list[str]) -> list[str]:
    assumptions: list[str] = []
    if "region" in missing:
        assumptions.append("Region is inferred rather than confirmed, so provider-specific filtering may differ.")
    if "provider_name" in missing:
        assumptions.append("Provider-specific heuristics are unknown, so ASN or ISP-specific advice is provisional.")
    if "provider_type" in missing:
        assumptions.append("Access path is assumed to be typical home broadband, not a constrained mobile network.")
    if "scope" in missing:
        assumptions.append("Scope is treated as day-to-day multi-service access, not a one-site bypass.")
    if "client_os" in missing and "router_model" in missing:
        assumptions.append("Endpoint constraints are unknown, so client compatibility still needs checking.")
    if not isinstance(case.get("current_stack"), dict) or not any((case.get("current_stack") or {}).values()):
        assumptions.append("The current protocol stack is unknown, so the recommendation is based on symptoms only.")
    return assumptions


def choose_confidence(scores: dict[str, int], missing: list[str]) -> str:
    ordered = sorted(scores.values(), reverse=True)
    top_score = ordered[0]
    second_score = ordered[1] if len(ordered) > 1 else 0
    if len(missing) > 3:
        return "low"
    if top_score >= 2 and top_score >= second_score + 1:
        return "high" if len(missing) <= 1 else "medium"
    return "medium"


def choose_routing_mode(case: dict, primary_contour: str, default_mode: str) -> str:
    needs_text = " ".join(str(item) for item in case.get("needs", []))
    scope = str(case.get("scope") or "").casefold()
    if "blocked only" in needs_text.casefold():
        return "blocked-only"
    if primary_contour == "Local DPI bypass":
        return "targeted-local-bypass"
    if scope in {"single-device", "single device"} and "few blocked sites" in needs_text.casefold():
        return "targeted-local-bypass"
    return default_mode


def triage_case(case: dict) -> dict:
    scores = score_failure_modes(case)
    mode = dominant_mode(case)
    missing = unknown_fields(case)
    assumptions = derive_assumptions(case, missing)
    confidence = choose_confidence(scores, missing)
    routing_mode = choose_routing_mode(case, mode.primary_contour, mode.routing_mode)

    result = {
        "classification": {
            "dominant_failure_mode": mode.key,
            "summary": mode.summary,
            "scoreboard": scores,
        },
        "recommendation": {
            "primary_contour": mode.primary_contour,
            "backup_contour": mode.backup_contour,
            "routing_mode": routing_mode,
            "live_intel_lane": mode.preferred_chat,
        },
        "confidence": confidence,
        "assumptions": assumptions,
        "unknown_fields": missing,
        "next_tests": list(mode.next_tests),
    }
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify a Russia connectivity case and emit a triage report")
    parser.add_argument("--input", required=True, help="Path to a JSON file with case facts")
    parser.add_argument("--output", help="Optional path to write the triage report as JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    case = json.loads(Path(args.input).expanduser().read_text(encoding="utf-8"))
    report = triage_case(case)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).expanduser().write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
