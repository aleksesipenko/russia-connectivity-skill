from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "analyze_telegram_intel.py"
SCRIPT_DIR = str(SCRIPT_PATH.parent)


def load_module():
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, SCRIPT_DIR)
    spec = importlib.util.spec_from_file_location("analyze_telegram_intel", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_package(name: str, messages: list[dict]) -> dict:
    return {
        "dialog": {"name": name},
        "counts": {
            "messages_in_window": len(messages),
            "pinned_messages": sum(1 for row in messages if "pinned" in row.get("export_tags", [])),
        },
        "messages": messages,
    }


class AnalyzeTelegramIntelTests(unittest.TestCase):
    def test_parse_local_date_accepts_iso_timestamps(self) -> None:
        module = load_module()
        parsed = module.parse_local_date("2026-05-15T09:41:26+03:00")
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 5)
        self.assertEqual(parsed.day, 15)

    def test_summary_includes_freshness_and_symptom_sections(self) -> None:
        module = load_module()
        vpn_package = make_package(
            "Обсуждение VPN-протоколов",
            [
                {
                    "id": 101,
                    "date_local": "2026-05-21 10:20",
                    "effective_text": "reality on 443 dies after first data, handshake works only through vpn",
                    "export_tags": [],
                },
                {
                    "id": 102,
                    "date_local": "2026-05-20 09:00",
                    "effective_text": "cloudflare subnets and asn look suspicious in rf",
                    "export_tags": ["pinned"],
                },
            ],
        )
        itdog_package = make_package(
            "ITDog Chat",
            [
                {
                    "id": 201,
                    "date_local": "2026-05-21 11:15",
                    "effective_text": "dnsmasq and fakeip broke router access, only russian resolvers fail",
                    "export_tags": [],
                },
                {
                    "id": 202,
                    "date_local": "2026-05-18 08:40",
                    "effective_text": "awg on openwrt works, but udp unstable on one mobile operator",
                    "export_tags": [],
                },
            ],
        )

        summary_text, machine_summary = module.build_summary([vpn_package, itdog_package])

        self.assertIn("## Freshness", summary_text)
        self.assertIn("## Symptom Heatmap", summary_text)
        self.assertIn("dns-or-nsdi", summary_text)
        self.assertIn("443-tls-policing", summary_text)
        self.assertIn("fresh_examples", machine_summary)
        self.assertIn("symptom_counts", machine_summary)
        self.assertEqual(machine_summary["fresh_examples"]["dns-or-nsdi"][0]["chat"], "ITDog Chat")


if __name__ == "__main__":
    unittest.main()
