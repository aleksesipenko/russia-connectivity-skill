from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "triage_case.py"
SCRIPT_DIR = str(SCRIPT_PATH.parent)


def load_module():
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, SCRIPT_DIR)
    spec = importlib.util.spec_from_file_location("triage_case", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TriageCaseTests(unittest.TestCase):
    def test_dns_symptom_prefers_itdog_and_awg(self) -> None:
        module = load_module()
        result = module.triage_case(
            {
                "provider_type": "home",
                "scope": "router",
                "symptoms": ["dns", "domain disappears on russian resolvers"],
                "needs": ["whole-network coverage"],
            }
        )

        self.assertEqual(result["classification"]["dominant_failure_mode"], "dns-or-nsdi")
        self.assertEqual(result["recommendation"]["primary_contour"], "AmneziaWG 2.0")
        self.assertEqual(result["recommendation"]["live_intel_lane"], "ITDog Chat")
        self.assertEqual(result["recommendation"]["routing_mode"], "all-except-ru")
        self.assertEqual(result["confidence"], "medium")

    def test_443_tls_symptom_marks_reality_primary_and_udp_backup(self) -> None:
        module = load_module()
        result = module.triage_case(
            {
                "provider_type": "home",
                "scope": "single-device",
                "symptoms": ["works until first data", "only on 443", "reality"],
                "current_stack": {"protocol": "VLESS", "transport": "REALITY", "port": 443},
            }
        )

        self.assertEqual(result["classification"]["dominant_failure_mode"], "443-tls-policing")
        self.assertEqual(result["recommendation"]["primary_contour"], "Xray VLESS + REALITY")
        self.assertEqual(result["recommendation"]["backup_contour"], "AmneziaWG 2.0")
        self.assertEqual(result["recommendation"]["live_intel_lane"], "Обсуждение VPN-протоколов")
        self.assertIn("alternate port", result["next_tests"][0].casefold())

    def test_many_unknowns_lower_confidence_and_surface_assumptions(self) -> None:
        module = load_module()
        result = module.triage_case({"symptoms": ["blocked sites"]})

        self.assertEqual(result["confidence"], "low")
        self.assertGreaterEqual(len(result["assumptions"]), 3)
        self.assertTrue(result["unknown_fields"])

    def test_cli_writes_json_report(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "case.json"
            output_path = Path(tmp_dir) / "report.json"
            input_path.write_text(
                json.dumps(
                    {
                        "provider_type": "mobile",
                        "scope": "single-device",
                        "symptoms": ["udp unstable", "quic blocked"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            exit_code = module.main(
                [
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["classification"]["dominant_failure_mode"], "udp-instability")
            self.assertEqual(report["recommendation"]["primary_contour"], "Xray VLESS + REALITY")


if __name__ == "__main__":
    unittest.main()
