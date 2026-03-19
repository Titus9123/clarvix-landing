import logging
from uuid import UUID

from backend.agents.ai_revenue.action_planning import ActionPlanningAgent
from backend.agents.ai_revenue.anomaly_detection import AnomalyDetectionAgent
from backend.agents.ai_revenue.optimization_strategy import OptimizationStrategyAgent
from backend.agents.ai_revenue.report_structuring import ReportStructuringAgent
from backend.agents.ai_revenue.revenue_opportunity import RevenueOpportunityAgent
from backend.agents.ai_revenue.revenue_data_source import DeterministicRevenueDataSource
from backend.agents.ai_revenue.revenue_monitoring import RevenueMonitoringAgent
from backend.agents.ai_revenue.simulation import SimulationAgent
from backend.core.errors import AppError
from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.common import RequestStatus, RunStatus, ServiceType, WorkflowRunCreate, WorkflowRunOut
from backend.services.run_manager import RunManager


logger = logging.getLogger(__name__)


class AIRevenueWorkflowService:
    def __init__(
        self,
        request_repo: ServiceRequestRepository,
        run_repo: WorkflowRunRepository,
        report_repo: ReportRepository,
        run_manager: RunManager,
    ) -> None:
        self.request_repo = request_repo
        self.run_repo = run_repo
        self.run_manager = run_manager
        self.data_source = DeterministicRevenueDataSource(report_repo=report_repo)
        self.monitoring_agent = RevenueMonitoringAgent()
        self.anomaly_agent = AnomalyDetectionAgent()
        self.opportunity_agent = RevenueOpportunityAgent()
        self.strategy_agent = OptimizationStrategyAgent()
        self.action_planning_agent = ActionPlanningAgent()
        self.simulation_agent = SimulationAgent()
        self.structuring_agent = ReportStructuringAgent()

    @staticmethod
    def _average_order_value_hint(input_payload: dict) -> float:
        raw_value = input_payload.get("average_order_value")
        if isinstance(raw_value, (int, float)) and raw_value > 0:
            return float(raw_value)
        return 120.0

    def execute_for_request(self, request_id: UUID) -> WorkflowRunOut:
        request = self.request_repo.get(request_id)
        if request.service_type != ServiceType.AI_REVENUE_OPTIMIZATION:
            raise AppError(
                "service_type_mismatch",
                "Requested workflow execution is only available for ai_revenue_optimization",
                400,
            )
        if not request.website_url:
            raise AppError("missing_website_url", "website_url is required for AI Revenue workflow", 400)

        self.request_repo.update_status(request_id, RequestStatus.IN_REVIEW)
        run = self.run_repo.create(
            WorkflowRunCreate(
                request_id=request.id,
                run_input={
                    "website_url": request.website_url,
                    "business_description": request.business_description,
                    "revenue_model": request.revenue_model,
                    "main_concern": request.main_concern,
                    "input_payload": request.input_payload,
                },
            )
        )

        try:
            run = self.run_manager.transition(run.id, RunStatus.RUNNING, run_output={"phase": "running"})

            data_snapshot = self.data_source.get_snapshot(request)
            monitoring = self.monitoring_agent.run(
                data_snapshot=data_snapshot,
                primary_concern=request.main_concern,
                average_order_value_hint=self._average_order_value_hint(request.input_payload),
            )
            anomaly_output = self.anomaly_agent.run(
                current_state=monitoring.current_state,
                data_snapshot=data_snapshot,
            )
            revenue_findings = self.opportunity_agent.run(
                anomalies=anomaly_output.anomalies,
                current_state=monitoring.current_state,
                business_description=request.business_description,
                revenue_model=request.revenue_model,
                main_concern=request.main_concern,
            )
            strategy_output = self.strategy_agent.run(
                anomalies=anomaly_output.anomalies,
                leaks=revenue_findings.revenue_leaks,
                opportunities=revenue_findings.opportunities,
            )
            planning_output = self.action_planning_agent.run(
                decisions=strategy_output.decisions,
            )
            simulation_output = self.simulation_agent.run(
                current_state=monitoring.current_state,
                optimization_actions=planning_output.optimization_actions,
            )
            report = self.structuring_agent.build_report(
                request_id=request.id,
                current_state=monitoring.current_state,
                detected_anomalies=anomaly_output.anomalies,
                revenue_leaks=revenue_findings.revenue_leaks,
                optimization_actions=planning_output.optimization_actions,
                execution_plan=planning_output.execution_plan,
                estimated_revenue_gain=simulation_output.estimated_revenue_gain,
            )
            markdown = self.structuring_agent.build_markdown(report)

            run_output = {
                "report_json": report.model_dump(mode="json"),
                "report_markdown": markdown,
                "data_snapshot": {
                    "traffic_metrics": data_snapshot.traffic_metrics,
                    "conversion_metrics": data_snapshot.conversion_metrics,
                    "funnel_signals": data_snapshot.funnel_signals,
                    "audit_signals": data_snapshot.audit_signals,
                },
                "current_state": report.current_state.model_dump(mode="json"),
                "detected_anomalies": [item.model_dump(mode="json") for item in report.detected_anomalies],
                "revenue_leaks": [item.model_dump(mode="json") for item in report.revenue_leaks],
                "optimization_actions": [item.model_dump(mode="json") for item in report.optimization_actions],
                "execution_plan": [item.model_dump(mode="json") for item in report.execution_plan],
                "estimated_revenue_gain": report.estimated_revenue_gain.model_dump(mode="json"),
            }
            run = self.run_manager.transition(run.id, RunStatus.NEEDS_REVIEW, run_output=run_output)
            self.request_repo.update_status(request_id, RequestStatus.IN_REVIEW)
            return run
        except Exception as exc:
            logger.exception("ai_revenue_workflow_failed", extra={"request_id": str(request_id)})
            self.run_manager.transition(
                run.id,
                RunStatus.FAILED,
                run_output={"phase": "failed"},
                error_message=str(exc),
            )
            self.request_repo.update_status(request_id, RequestStatus.FAILED)
            raise
