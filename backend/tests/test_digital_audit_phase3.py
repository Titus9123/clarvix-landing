import tempfile
import unittest
from pathlib import Path

from backend.core.errors import AppError
from backend.db import database
from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.common import RunStatus, ServiceRequestCreate, ServiceType
from backend.schemas.digital_audit import DigitalAuditReportV1
from backend.services.digital_audit_workflow import DigitalAuditWorkflowService
from backend.services.report_validation import ReportValidationService
from backend.services.run_lifecycle import RunLifecycleService
from backend.services.run_manager import RunManager


class TestDigitalAuditPhase3(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.temp_dir.name) / "test_ops_phase3.db"
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

    def _create_request(self):
        return self.request_repo.create(
            ServiceRequestCreate(
                service_type=ServiceType.DIGITAL_AUDIT,
                client_name="Clarvix Demo Client",
                website_url="https://demo.example.com/services/audit",
                business_description="B2B consulting firm focused on inbound leads",
                revenue_model="Project fees with monthly retainer upsell",
                main_concern="Lead quality and conversion consistency",
                input_payload={"segment": "b2b_services"},
            )
        )

    def test_full_digital_audit_run_flow(self) -> None:
        req = self._create_request()
        run = self.workflow.execute_for_request(req.id)

        self.assertEqual(run.run_status, RunStatus.NEEDS_REVIEW)
        self.assertIn("input_sources", run.run_output)
        self.assertIn("scan_context", run.run_output)
        self.assertIn("agent_outputs", run.run_output)
        self.assertIn("final_report", run.run_output)
        self.assertIn("validation_status", run.run_output)
        self.assertIn("metrics_snapshot", run.run_output)
        self.assertIn("report_json", run.run_output["final_report"])
        self.assertIn("report_markdown", run.run_output["final_report"])
        self.assertEqual(
            run.run_output["final_report"]["report_json"]["schema_version"],
            "digital_audit_report_v1",
        )
        self.assertIn("findings", run.run_output["final_report"]["report_json"])
        self.assertIn("action_plan", run.run_output["final_report"]["report_json"])
        self.assertTrue(run.run_output["validation_status"]["valid"])

    def test_schema_validation_failure(self) -> None:
        req = self._create_request()
        run = self.workflow.execute_for_request(req.id)
        invalid_report = dict(run.run_output["final_report"]["report_json"])
        invalid_report.pop("scoring", None)

        with self.assertRaises(AppError) as ctx:
            self.validator.validate(ServiceType.DIGITAL_AUDIT, invalid_report)
        self.assertEqual(ctx.exception.code, "invalid_report_payload")

    def test_transition_to_needs_review(self) -> None:
        req = self._create_request()
        run = self.workflow.execute_for_request(req.id)
        self.assertEqual(run.run_status, RunStatus.NEEDS_REVIEW)
        self.assertEqual(self.request_repo.get(req.id).status.value, "in_review")

    def test_approval_path_reuse(self) -> None:
        req = self._create_request()
        run = self.workflow.execute_for_request(req.id)

        approved = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            run_output=run.run_output,
        )
        self.assertEqual(approved.run_status, RunStatus.APPROVED)
        self.assertEqual(self.request_repo.get(req.id).status.value, "completed")
        self.assertEqual(len(self.report_repo.list()), 1)
        stored_report = self.report_repo.list()[0]
        DigitalAuditReportV1.model_validate(stored_report.report_json)

    def test_deterministic_output(self) -> None:
        req = self._create_request()
        run1 = self.workflow.execute_for_request(req.id)
        run2 = self.workflow.execute_for_request(req.id)

        self.assertEqual(
            run1.run_output["final_report"]["report_json"],
            run2.run_output["final_report"]["report_json"],
        )
        self.assertEqual(
            run1.run_output["final_report"]["report_markdown"],
            run2.run_output["final_report"]["report_markdown"],
        )
        self.assertEqual(run1.run_output["metrics_snapshot"], run2.run_output["metrics_snapshot"])


if __name__ == "__main__":
    unittest.main()
