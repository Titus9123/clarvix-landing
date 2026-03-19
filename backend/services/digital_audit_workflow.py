import logging
from uuid import UUID

from backend.agents.digital_audit.audit_scoring import AuditScoringAgent
from backend.agents.digital_audit.performance import PerformanceAgent
from backend.agents.digital_audit.report_structuring import AuditReportStructuringAgent
from backend.agents.digital_audit.tracking_integrity import TrackingIntegrityAgent
from backend.agents.digital_audit.trust_signal import TrustSignalAgent
from backend.agents.digital_audit.website_structure import WebsiteStructureAgent
from backend.core.errors import AppError
from backend.db.repositories import ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.common import RequestStatus, RunStatus, ServiceType, WorkflowRunCreate, WorkflowRunOut
from backend.services.report_validation import ReportValidationService
from backend.services.run_manager import RunManager
from backend.tools.internal_metrics import build_mock_metrics
from backend.tools.scan_input_loader import ScanInputLoader


logger = logging.getLogger(__name__)


class DigitalAuditWorkflowService:
    """
    Deterministic Digital Presence Audit workflow (no external APIs, no LLMs).
    Metrics tool path in V1: in-process deterministic provider `build_mock_metrics`.
    """

    def __init__(
        self,
        request_repo: ServiceRequestRepository,
        run_repo: WorkflowRunRepository,
        run_manager: RunManager,
        report_validator: ReportValidationService,
        scan_loader: ScanInputLoader | None = None,
    ) -> None:
        self.request_repo = request_repo
        self.run_repo = run_repo
        self.run_manager = run_manager
        self.report_validator = report_validator
        self.structure_agent = WebsiteStructureAgent()
        self.tracking_agent = TrackingIntegrityAgent()
        self.performance_agent = PerformanceAgent()
        self.trust_agent = TrustSignalAgent()
        self.scoring_agent = AuditScoringAgent()
        self.report_agent = AuditReportStructuringAgent()
        self.scan_loader = scan_loader or ScanInputLoader()

    def _log_stage(self, event: str, request_id: UUID, run_id: UUID, stage: str, payload: dict | None = None) -> None:
        logger.info(
            event,
            extra={
                "request_id": str(request_id),
                "run_id": str(run_id),
                "stage": stage,
                "payload": payload or {},
            },
        )

    def execute_for_request(self, request_id: UUID) -> WorkflowRunOut:
        request = self.request_repo.get(request_id)
        if request.service_type != ServiceType.DIGITAL_AUDIT:
            raise AppError(
                "service_type_mismatch",
                "Requested workflow execution is only available for digital_audit",
                400,
            )
        if not request.website_url:
            raise AppError("missing_website_url", "website_url is required for Digital Audit workflow", 400)

        self.request_repo.update_status(request_id, RequestStatus.IN_REVIEW)
        run = self.run_repo.create(
            WorkflowRunCreate(
                request_id=request.id,
                run_input={
                    "website_url": request.website_url,
                    "business_description": request.business_description,
                    "main_concern": request.main_concern,
                    "input_payload": request.input_payload,
                },
            )
        )

        try:
            run = self.run_manager.transition(run.id, RunStatus.RUNNING, run_output={"phase": "running"})
            self._log_stage("agent_start", request.id, run.id, "scan_input_loader")

            scan_context = self.scan_loader.build_context()
            self._log_stage(
                "agent_output",
                request.id,
                run.id,
                "scan_input_loader",
                {
                    "input_sources_count": len(scan_context.input_sources),
                    "template_blocks": scan_context.template_blocks,
                    "sections_present": scan_context.sections_present,
                    "findings_count_hint": scan_context.findings_count_hint,
                },
            )

            metrics = build_mock_metrics(request.website_url)
            self._log_stage("agent_output", request.id, run.id, "metrics", metrics.model_dump(mode="json"))

            self._log_stage("agent_start", request.id, run.id, "website_structure")
            structure = self.structure_agent.run(request.website_url)
            self._log_stage("agent_output", request.id, run.id, "website_structure", structure.model_dump(mode="json"))

            self._log_stage("agent_start", request.id, run.id, "tracking_integrity")
            tracking = self.tracking_agent.run(request.website_url)
            self._log_stage("agent_output", request.id, run.id, "tracking_integrity", tracking.model_dump(mode="json"))

            self._log_stage("agent_start", request.id, run.id, "performance")
            performance = self.performance_agent.run(request.website_url)
            self._log_stage("agent_output", request.id, run.id, "performance", performance.model_dump(mode="json"))

            self._log_stage("agent_start", request.id, run.id, "trust_signal")
            trust = self.trust_agent.run(request.website_url, request.business_description)
            self._log_stage("agent_output", request.id, run.id, "trust_signal", trust.model_dump(mode="json"))

            self._log_stage("agent_start", request.id, run.id, "audit_scoring")
            scoring = self.scoring_agent.run(
                structure=structure,
                tracking=tracking,
                performance=performance,
                trust=trust,
            )
            self._log_stage("scoring_result", request.id, run.id, "audit_scoring", scoring.model_dump(mode="json"))

            self._log_stage("agent_start", request.id, run.id, "report_structuring")
            report = self.report_agent.run(
                request_id=request.id,
                website_url=request.website_url,
                business_description=request.business_description,
                main_concern=request.main_concern,
                structure=structure,
                tracking=tracking,
                performance=performance,
                trust=trust,
                scoring=scoring,
                scan_context=scan_context,
            )
            self._log_stage(
                "agent_output",
                request.id,
                run.id,
                "report_structuring",
                {
                    "report_schema_version": report.report_json.get("schema_version"),
                    "findings_count": len(report.report_json.get("findings", [])),
                    "action_plan_count": len(report.report_json.get("action_plan", [])),
                },
            )

            # Enforce strict schema before the run reaches review.
            validated_report_json = self.report_validator.validate(
                ServiceType.DIGITAL_AUDIT,
                report.report_json,
            )
            validation_status = {
                "service_type": ServiceType.DIGITAL_AUDIT.value,
                "schema_version": validated_report_json.get("schema_version"),
                "valid": True,
            }
            self._log_stage("validation_result", request.id, run.id, "report_validation", validation_status)

            run_output = {
                "input_sources": scan_context.input_sources,
                "scan_context": scan_context.model_dump(mode="json"),
                "agent_outputs": {
                    "website_structure": structure.model_dump(mode="json"),
                    "tracking_integrity": tracking.model_dump(mode="json"),
                    "performance": performance.model_dump(mode="json"),
                    "trust_signal": trust.model_dump(mode="json"),
                    "audit_scoring": scoring.model_dump(mode="json"),
                    "report_structuring": {
                        "findings_count": len(validated_report_json.get("findings", [])),
                        "action_plan_count": len(validated_report_json.get("action_plan", [])),
                    },
                },
                "final_report": {
                    "report_json": validated_report_json,
                    "report_markdown": report.report_markdown,
                },
                "validation_status": validation_status,
                "report_json": validated_report_json,
                "report_markdown": report.report_markdown,
                "metrics_snapshot": metrics.model_dump(mode="json"),
            }
            run = self.run_manager.transition(run.id, RunStatus.NEEDS_REVIEW, run_output=run_output)
            self.request_repo.update_status(request_id, RequestStatus.IN_REVIEW)
            return run
        except Exception as exc:
            logger.exception("digital_audit_workflow_failed", extra={"request_id": str(request_id)})
            self.run_manager.transition(
                run.id,
                RunStatus.FAILED,
                run_output={"phase": "failed"},
                error_message=str(exc),
            )
            self.request_repo.update_status(request_id, RequestStatus.FAILED)
            raise
