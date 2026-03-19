import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.core.errors import AppError
from backend.db import database
from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.ai_revenue import AIRevenueReportV1
from backend.schemas.common import (
    RunStatus,
    ServiceRequestCreate,
    ServiceType,
    WorkflowRunCreate,
)
from backend.services.ai_revenue_workflow import AIRevenueWorkflowService
from backend.services.report_validation import ReportValidationService
from backend.services.run_lifecycle import RunLifecycleService
from backend.services.run_manager import RunManager
from backend.tools.internal_metrics import InternalMetricsResponse


class TestAIRevenuePhase2(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = Path(self.temp_dir.name) / "test_ops.db"
        database.init_db()

        self.request_repo = ServiceRequestRepository()
        self.run_repo = WorkflowRunRepository(request_repo=self.request_repo)
        self.report_repo = ReportRepository()
        self.run_manager = RunManager(run_repo=self.run_repo)
        self.report_validator = ReportValidationService()
        self.lifecycle = RunLifecycleService(
            run_manager=self.run_manager,
            run_repo=self.run_repo,
            request_repo=self.request_repo,
            report_repo=self.report_repo,
            report_validator=self.report_validator,
        )
        self.workflow = AIRevenueWorkflowService(
            request_repo=self.request_repo,
            run_repo=self.run_repo,
            run_manager=self.run_manager,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_ai_request(self):
        return self.request_repo.create(
            ServiceRequestCreate(
                service_type=ServiceType.AI_REVENUE_OPTIMIZATION,
                client_name="Acme Corp",
                website_url="https://acme.test/pricing",
                business_description="B2B services company with inbound lead funnel",
                revenue_model="Monthly retainer plus setup fee",
                main_concern="Lead conversion is low after landing visits",
                input_payload={"industry": "B2B services"},
            )
        )

    def _valid_report_json(self, request_id):
        return AIRevenueReportV1(
            request_id=request_id,
            summary="Revenue leakage and opportunity patterns were detected in deterministic checks.",
            top_issues=[
                {
                    "issue": "Primary CTA underperforms",
                    "impact": "high",
                    "confidence": 0.82,
                    "evidence": ["Low CTA visibility score"],
                    "reasoning": "Strong signal in conversion hints.",
                }
            ],
            opportunities=[
                {
                    "opportunity": "Improve CTA placement",
                    "expected_effect": "Increase conversion starts",
                    "effort": "low",
                    "confidence": 0.76,
                }
            ],
            action_plan=[
                {
                    "priority": "P1",
                    "action": "Refine CTA hierarchy on key pages",
                    "owner": "web",
                    "timeline": "7 days",
                }
            ],
            review={"status": "needs_review", "reviewed_by": None, "review_notes": None},
        ).model_dump(mode="json")

    def test_ai_revenue_workflow_happy_path(self) -> None:
        req = self._create_ai_request()
        run = self.workflow.execute_for_request(req.id)
        self.assertEqual(run.run_status, RunStatus.NEEDS_REVIEW)
        self.assertIn("report_json", run.run_output)
        self.assertIn("report_markdown", run.run_output)
        self.assertEqual(run.run_output["report_json"]["schema_version"], "ai_revenue_report_v1")
        self.assertTrue(run.run_output["report_markdown"].startswith("# AI Revenue Optimization Audit"))

    def test_metrics_tool_path_is_in_process_provider(self) -> None:
        req = self._create_ai_request()
        fake_metrics = InternalMetricsResponse(
            traffic_estimate=3200,
            conversion_signals={"cta_visibility_score": 0.7, "checkout_dropoff_risk": 0.4},
            engagement_signals={"bounce_risk_hint": 0.3, "avg_session_depth_hint": 2.2},
        )
        with patch("backend.services.ai_revenue_workflow.build_mock_metrics", return_value=fake_metrics) as mocked:
            run = self.workflow.execute_for_request(req.id)
            mocked.assert_called_once_with(req.website_url)
            self.assertEqual(run.run_output["metrics_snapshot"]["traffic_estimate"], 3200)

    def test_report_schema_validation_failure(self) -> None:
        with self.assertRaises(AppError) as ctx:
            self.report_validator.validate(
                ServiceType.AI_REVENUE_OPTIMIZATION,
                {"schema_version": "ai_revenue_report_v1", "summary": "too_short"},
            )
        self.assertEqual(ctx.exception.code, "invalid_report_payload")

    def test_run_lifecycle_to_approved_creates_report(self) -> None:
        req = self._create_ai_request()
        run = self.run_repo.create(WorkflowRunCreate(request_id=req.id, run_input={"seed": "manual"}))

        running = self.lifecycle.transition(run.id, RunStatus.RUNNING, {"phase": "running"})
        self.assertEqual(running.run_status, RunStatus.RUNNING)

        report_json = self._valid_report_json(req.id)

        needs_review = self.lifecycle.transition(
            run.id,
            RunStatus.NEEDS_REVIEW,
            {"report_json": report_json, "report_markdown": "# AI Revenue Optimization Audit\n\nReviewed."},
        )
        self.assertEqual(needs_review.run_status, RunStatus.NEEDS_REVIEW)

        approved = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            {"report_json": report_json, "report_markdown": "# AI Revenue Optimization Audit\n\nReviewed."},
        )
        self.assertEqual(approved.run_status, RunStatus.APPROVED)
        self.assertEqual(len(self.report_repo.list()), 1)
        self.assertEqual(self.request_repo.get(req.id).status.value, "completed")

    def test_duplicate_approval_is_safe_noop(self) -> None:
        req = self._create_ai_request()
        run = self.run_repo.create(WorkflowRunCreate(request_id=req.id, run_input={"seed": "manual"}))
        report_json = self._valid_report_json(req.id)

        self.lifecycle.transition(run.id, RunStatus.RUNNING, {"phase": "running"})
        self.lifecycle.transition(
            run.id,
            RunStatus.NEEDS_REVIEW,
            {"report_json": report_json, "report_markdown": "# AI Revenue Optimization Audit\n\nReviewed."},
        )
        first_approval = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            {"report_json": report_json, "report_markdown": "# AI Revenue Optimization Audit\n\nReviewed."},
        )
        second_approval = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            {"report_json": report_json, "report_markdown": "# AI Revenue Optimization Audit\n\nReviewed."},
        )

        self.assertEqual(first_approval.run_status, RunStatus.APPROVED)
        self.assertEqual(second_approval.run_status, RunStatus.APPROVED)
        self.assertEqual(len(self.report_repo.list()), 1)

    def test_atomic_approval_validation_failure_keeps_state_consistent(self) -> None:
        req = self._create_ai_request()
        run = self.run_repo.create(WorkflowRunCreate(request_id=req.id, run_input={"seed": "manual"}))

        self.lifecycle.transition(run.id, RunStatus.RUNNING, {"phase": "running"})
        self.lifecycle.transition(
            run.id,
            RunStatus.NEEDS_REVIEW,
            {
                "report_json": self._valid_report_json(req.id),
                "report_markdown": "# AI Revenue Optimization Audit\n\nDraft ready.",
            },
        )

        with self.assertRaises(AppError) as ctx:
            self.lifecycle.transition(
                run.id,
                RunStatus.APPROVED,
                {"report_json": {"schema_version": "ai_revenue_report_v1"}, "report_markdown": "ok markdown"},
            )
        self.assertEqual(ctx.exception.code, "invalid_report_payload")

        run_after = self.run_repo.get(run.id)
        self.assertEqual(run_after.run_status, RunStatus.NEEDS_REVIEW)
        self.assertEqual(self.request_repo.get(req.id).status.value, "in_review")
        self.assertEqual(len(self.report_repo.list()), 0)


if __name__ == "__main__":
    unittest.main()
