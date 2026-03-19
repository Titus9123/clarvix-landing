import tempfile
import unittest
from pathlib import Path

from backend.db import database
from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.common import RunStatus, ServiceRequestCreate, ServiceType
from backend.services.digital_audit_workflow import DigitalAuditWorkflowService
from backend.services.report_validation import ReportValidationService
from backend.services.run_lifecycle import RunLifecycleService
from backend.services.run_manager import RunManager
from backend.tools.scan_input_loader import SCANS_DIR


class TestDigitalAuditRealExecution(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.temp_dir.name) / "test_ops_phase3_real.db"
        database.init_db()

        self.request_repo = ServiceRequestRepository()
        self.run_repo = WorkflowRunRepository(request_repo=self.request_repo)
        self.report_repo = ReportRepository()
        self.run_manager = RunManager(run_repo=self.run_repo)
        self.validator = ReportValidationService()
        self.lifecycle = RunLifecycleService(
            run_manager=self.run_manager,
            run_repo=self.run_repo,
            request_repo=self.request_repo,
            report_repo=self.report_repo,
            report_validator=self.validator,
        )
        self.workflow = DigitalAuditWorkflowService(
            request_repo=self.request_repo,
            run_repo=self.run_repo,
            run_manager=self.run_manager,
            report_validator=self.validator,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @unittest.skipUnless(SCANS_DIR.exists(), "Scans directory is required for real execution test")
    def test_real_input_execution_visibility_and_approval_reuse(self) -> None:
        req = self.request_repo.create(
            ServiceRequestCreate(
                service_type=ServiceType.DIGITAL_AUDIT,
                client_name="Real Input Client",
                website_url="https://www.clarvix.net",
                business_description="Real execution path backed by Scans evidence files.",
                revenue_model="Services + recurring retainers",
                main_concern="Need fully visible deterministic workflow execution",
                input_payload={"source": "real_scans"},
            )
        )

        run = self.workflow.execute_for_request(req.id)
        self.assertEqual(run.run_status, RunStatus.NEEDS_REVIEW)
        self.assertTrue(run.run_output["input_sources"])
        self.assertIn("scan_context", run.run_output)
        self.assertIn("agent_outputs", run.run_output)
        self.assertIn("final_report", run.run_output)
        self.assertTrue(run.run_output["validation_status"]["valid"])

        run_second = self.workflow.execute_for_request(req.id)
        self.assertEqual(
            run.run_output["final_report"]["report_json"],
            run_second.run_output["final_report"]["report_json"],
        )

        approved = self.lifecycle.transition(run.id, RunStatus.APPROVED, run_output=run.run_output)
        self.assertEqual(approved.run_status, RunStatus.APPROVED)
        approved_reuse = self.lifecycle.transition(run.id, RunStatus.APPROVED, run_output=run.run_output)
        self.assertEqual(approved_reuse.run_status, RunStatus.APPROVED)
        self.assertEqual(len(self.report_repo.list()), 1)


if __name__ == "__main__":
    unittest.main()
