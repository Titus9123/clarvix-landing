from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.common import ServiceType
from backend.tools.scan_input_loader import SCANS_DIR, ScanInputLoader


def _load_sample_payload(scans_dir: Path) -> dict:
    raw_files = sorted(scans_dir.glob("*_raw*.json"))
    sample_name = "Miami Realty Solution"
    website_url = "https://www.clarvix.net"
    business_description = "Real-estate digital presence audit based on real Clarvix scan artifacts."
    main_concern = "Need a deterministic visibility-first audit with structured findings."

    if raw_files:
        raw_path = raw_files[0]
        sample_name = raw_path.stem.replace("_raw_", "").replace("_", " ").title()
        try:
            raw_data = json.loads(raw_path.read_text(encoding="utf-8", errors="ignore"))
            competitors = raw_data.get("competitors", [])
            if competitors and isinstance(competitors[0], dict) and competitors[0].get("url"):
                website_url = competitors[0]["url"]
            score_hint = raw_data.get("psi", {}).get("mobile", {}).get("psi", 0)
            business_description = (
                "Real scan context loaded from Scans folder; "
                f"mobile performance hint={score_hint}; "
                f"competitor count={len(competitors)}."
            )
        except Exception:
            pass

    return {
        "service_type": ServiceType.DIGITAL_AUDIT.value,
        "client_name": sample_name,
        "website_url": website_url,
        "business_description": business_description,
        "revenue_model": "Project-based services and recurring retainers",
        "main_concern": main_concern,
        "input_payload": {
            "sample_source": "Scans folder",
            "scans_dir": str(scans_dir),
        },
    }


def main() -> None:
    scan_loader = ScanInputLoader()
    scan_context = scan_loader.build_context()
    if not scan_context.input_sources:
        raise RuntimeError(f"No scan inputs found under {SCANS_DIR}")

    payload = _load_sample_payload(SCANS_DIR)

    with TestClient(app) as client:
        create_resp = client.post("/requests", json=payload)
        create_resp.raise_for_status()
        request_id = create_resp.json()["id"]

        run_resp = client.post(f"/runs/execute/digital-audit/{request_id}")
        run_resp.raise_for_status()
        run_id = run_resp.json()["id"]

        run_detail_resp = client.get(f"/runs/{run_id}")
        run_detail_resp.raise_for_status()
        run = run_detail_resp.json()

    report = run["run_output"]["final_report"]["report_json"]
    validation_status = run["run_output"]["validation_status"]
    overall_score = report["scoring"]["overall_score"]
    findings_count = len(report["findings"])
    issues_count = len(report["prioritized_issues"])

    print(f"run_id: {run_id}")
    print(f"overall_score: {overall_score}")
    print(f"findings_count: {findings_count}")
    print(f"issues_count: {issues_count}")
    print(f"validation_status: {validation_status}")
    print(f"final_run_status: {run['run_status']}")


if __name__ == "__main__":
    main()
