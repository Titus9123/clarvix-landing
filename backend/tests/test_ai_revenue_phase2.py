import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.core.errors import AppError
from backend.db import database
from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.ai_revenue import AIRevenueOperationalReportV2
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
            report_repo=self.report_repo,
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
        return AIRevenueOperationalReportV2(
            request_id=request_id,
            current_state={
                "traffic_estimate": 3200,
                "cta_visibility_score": 0.4,
                "checkout_dropoff_risk": 0.8,
                "bounce_risk_hint": 0.7,
                "avg_session_depth_hint": 1.3,
                "tracking_coverage_score": 0.45,
                "funnel_integrity_score": 0.31,
                "baseline_conversion_rate": 0.13,
                "observed_conversion_rate": 0.08,
                "baseline_average_order_value": 129.6,
                "observed_average_order_value": 120.0,
                "estimated_monthly_revenue": 30720.0,
                "primary_concern": "Lead conversion is low after landing visits",
            },
            detected_anomalies=[
                {
                    "anomaly_code": "conversion_drop",
                    "severity": "high",
                    "metric": "conversion_rate",
                    "observed_value": 0.08,
                    "expected_value": 0.13,
                    "delta": -0.05,
                    "reason": "Observed conversion rate is below deterministic baseline threshold.",
                }
            ],
            revenue_leaks=[
                {
                    "leak_code": "conv_drop_leak",
                    "description": "Conversion efficiency is below baseline and leaking qualified demand.",
                    "estimated_monthly_loss": 6758.4,
                    "confidence": 0.82,
                    "linked_anomalies": ["conversion_drop"],
                }
            ],
            optimization_actions=[
                {
                    "priority": "P1",
                    "action": "Recover baseline conversion efficiency",
                    "reason": "Conversion anomaly indicates direct revenue leakage from existing demand.",
                    "expected_impact": "Reduce checkout and CTA abandonment in high-intent sessions.",
                    "execution_steps": [
                        "Reorder CTA hierarchy on top-entry pages by intent depth.",
                        "Reduce non-essential checkout/form fields to minimum viable path.",
                    ],
                }
            ],
            execution_plan=[
                {
                    "sequence": 1,
                    "action": "Recover baseline conversion efficiency",
                    "priority": "P1",
                    "owner": "web",
                    "eta_days": 10,
                    "dependency": None,
                }
            ],
            estimated_revenue_gain={
                "conservative_monthly_gain": 1200.0,
                "likely_monthly_gain": 2000.0,
                "optimistic_monthly_gain": 2700.0,
                "confidence_note": "Simulation uses bounded deterministic heuristics and returns directional ranges.",
                "assumptions": ["Stable traffic quality in execution window."],
            },
            review={"status": "needs_review", "reviewed_by": None, "review_notes": None},
        ).model_dump(mode="json")

    def test_ai_revenue_workflow_happy_path(self) -> None:
        req = self._create_ai_request()
        run = self.workflow.execute_for_request(req.id)
        self.assertEqual(run.run_status, RunStatus.NEEDS_REVIEW)
        self.assertIn("report_json", run.run_output)
        self.assertIn("report_markdown", run.run_output)
        self.assertEqual(run.run_output["report_json"]["schema_version"], "ai_revenue_operational_v2")
        self.assertTrue(run.run_output["report_markdown"].startswith("# Revenue Agent Operational Output"))
        self.assertIn("current_state", run.run_output)
        self.assertIn("detected_anomalies", run.run_output)
        self.assertIn("optimization_actions", run.run_output)
        self.assertIn("execution_plan", run.run_output)

    def test_data_source_uses_in_process_metrics_provider(self) -> None:
        req = self._create_ai_request()
        fake_metrics = InternalMetricsResponse(
            traffic_estimate=3200,
            conversion_signals={"cta_visibility_score": 0.4, "checkout_dropoff_risk": 0.8},
            engagement_signals={"bounce_risk_hint": 0.7, "avg_session_depth_hint": 1.3},
        )
        with patch("backend.agents.ai_revenue.revenue_data_source.build_mock_metrics", return_value=fake_metrics) as mocked:
            run = self.workflow.execute_for_request(req.id)
            self.assertEqual(mocked.call_count, 3)
            mocked.assert_has_calls(
                [
                    unittest.mock.call(req.website_url),
                    unittest.mock.call(req.website_url),
                    unittest.mock.call(req.website_url),
                ]
            )
            self.assertEqual(run.run_output["data_snapshot"]["traffic_metrics"]["traffic_estimate"], 3200.0)

    def test_same_input_produces_same_operational_payload(self) -> None:
        req = self._create_ai_request()
        run_a = self.workflow.execute_for_request(req.id)
        run_b = self.workflow.execute_for_request(req.id)
        self.assertEqual(run_a.run_output["report_json"], run_b.run_output["report_json"])

    def test_anomalies_are_deterministic_and_explicit(self) -> None:
        req = self._create_ai_request()
        fake_metrics = InternalMetricsResponse(
            traffic_estimate=1400,
            conversion_signals={"cta_visibility_score": 0.2, "checkout_dropoff_risk": 0.92},
            engagement_signals={"bounce_risk_hint": 0.85, "avg_session_depth_hint": 1.0},
        )
        with patch("backend.agents.ai_revenue.revenue_data_source.build_mock_metrics", return_value=fake_metrics):
            run = self.workflow.execute_for_request(req.id)
        anomaly_codes = [item["anomaly_code"] for item in run.run_output["detected_anomalies"]]
        self.assertIn("conversion_drop", anomaly_codes)
        self.assertIn("traffic_mismatch", anomaly_codes)
        self.assertIn("missing_tracking", anomaly_codes)
        self.assertIn("broken_funnel", anomaly_codes)

    def test_action_plan_is_strategy_derived_not_static_template(self) -> None:
        req = self._create_ai_request()
        fake_metrics = InternalMetricsResponse(
            traffic_estimate=1400,
            conversion_signals={"cta_visibility_score": 0.25, "checkout_dropoff_risk": 0.88},
            engagement_signals={"bounce_risk_hint": 0.81, "avg_session_depth_hint": 1.1},
        )
        with patch("backend.agents.ai_revenue.revenue_data_source.build_mock_metrics", return_value=fake_metrics):
            run = self.workflow.execute_for_request(req.id)

        actions = run.run_output["optimization_actions"]
        self.assertGreaterEqual(len(actions), 1)
        self.assertNotIn(
            "Fix primary conversion friction and clarify CTA paths on top-entry pages",
            [item["action"] for item in actions],
        )
        for action in actions:
            self.assertGreaterEqual(len(action["execution_steps"]), 1)

    def test_report_schema_validation_failure(self) -> None:
        with self.assertRaises(AppError) as ctx:
            self.report_validator.validate(
                ServiceType.AI_REVENUE_OPTIMIZATION,
                {"schema_version": "ai_revenue_operational_v2"},
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
            {"report_json": report_json, "report_markdown": "# Revenue Agent Operational Output\n\nReviewed."},
        )
        self.assertEqual(needs_review.run_status, RunStatus.NEEDS_REVIEW)

        approved = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            {"report_json": report_json, "report_markdown": "# Revenue Agent Operational Output\n\nReviewed."},
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
            {"report_json": report_json, "report_markdown": "# Revenue Agent Operational Output\n\nReviewed."},
        )
        first_approval = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            {"report_json": report_json, "report_markdown": "# Revenue Agent Operational Output\n\nReviewed."},
        )
        second_approval = self.lifecycle.transition(
            run.id,
            RunStatus.APPROVED,
            {"report_json": report_json, "report_markdown": "# Revenue Agent Operational Output\n\nReviewed."},
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
                    "report_markdown": "# Revenue Agent Operational Output\n\nDraft ready.",
            },
        )

        with self.assertRaises(AppError) as ctx:
            self.lifecycle.transition(
                run.id,
                RunStatus.APPROVED,
                {"report_json": {"schema_version": "ai_revenue_operational_v2"}, "report_markdown": "ok markdown"},
            )
        self.assertEqual(ctx.exception.code, "invalid_report_payload")

        run_after = self.run_repo.get(run.id)
        self.assertEqual(run_after.run_status, RunStatus.NEEDS_REVIEW)
        self.assertEqual(self.request_repo.get(req.id).status.value, "in_review")
        self.assertEqual(len(self.report_repo.list()), 0)

    def test_markdown_adapter_is_consistent_with_operational_payload(self) -> None:
        req = self._create_ai_request()
        run = self.workflow.execute_for_request(req.id)
        payload = run.run_output["report_json"]
        markdown = run.run_output["report_markdown"]

        self.assertIn("Revenue Agent Operational Output", markdown)
        self.assertIn(str(payload["estimated_revenue_gain"]["likely_monthly_gain"]), markdown)
        for action in payload["optimization_actions"]:
            self.assertIn(action["action"], markdown)


if __name__ == "__main__":
    unittest.main()
