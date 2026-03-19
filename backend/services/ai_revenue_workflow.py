import logging
from uuid import UUID

from backend.agents.ai_revenue.prioritization import PrioritizationAgent
from backend.agents.ai_revenue.report_structuring import ReportStructuringAgent
from backend.agents.ai_revenue.revenue_opportunity import RevenueOpportunityAgent
from backend.agents.ai_revenue.website_analyzer import WebsiteAnalyzerAgent
from backend.core.errors import AppError
from backend.db.repositories import ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.common import RequestStatus, RunStatus, ServiceType, WorkflowRunCreate, WorkflowRunOut
from backend.services.run_manager import RunManager
from backend.tools.internal_metrics import build_mock_metrics


logger = logging.getLogger(__name__)


class AIRevenueWorkflowService:
    """
    V1 metrics tool path (explicit):
    - Uses in-process deterministic provider `build_mock_metrics`.
    - This is the single metrics source for workflow execution in V1.
    - Internal HTTP client path is intentionally not used here yet to avoid ambiguity.
    """

    def __init__(
        self,
        request_repo: ServiceRequestRepository,
        run_repo: WorkflowRunRepository,
        run_manager: RunManager,
    ) -> None:
        self.request_repo = request_repo
        self.run_repo = run_repo
        self.run_manager = run_manager
        self.website_analyzer = WebsiteAnalyzerAgent()
        self.opportunity_agent = RevenueOpportunityAgent()
        self.prioritization_agent = PrioritizationAgent()
        self.structuring_agent = ReportStructuringAgent()

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

            # Deterministic in-process metrics tool path for V1.
            metrics = build_mock_metrics(request.website_url)
            website_analysis = self.website_analyzer.run(request.website_url, metrics)
            revenue_findings = self.opportunity_agent.run(
                analyzer_output=website_analysis,
                business_description=request.business_description,
                revenue_model=request.revenue_model,
                main_concern=request.main_concern,
                metrics=metrics,
            )
            prioritized = self.prioritization_agent.run(
                issues=revenue_findings.revenue_issues,
                opportunities=revenue_findings.opportunities,
            )
            report = self.structuring_agent.build_report(
                request_id=request.id,
                analyzer_output=website_analysis,
                prioritized=prioritized,
                main_concern=request.main_concern,
            )
            markdown = self.structuring_agent.build_markdown(report)

            run_output = {
                "report_json": report.model_dump(mode="json"),
                "report_markdown": markdown,
                "metrics_snapshot": metrics.model_dump(mode="json"),
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
