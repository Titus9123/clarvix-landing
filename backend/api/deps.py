from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.services.ai_revenue_workflow import AIRevenueWorkflowService
from backend.services.digital_audit_workflow import DigitalAuditWorkflowService
from backend.services.report_validation import ReportValidationService
from backend.services.run_lifecycle import RunLifecycleService
from backend.services.run_manager import RunManager


request_repo = ServiceRequestRepository()
run_repo = WorkflowRunRepository(request_repo=request_repo)
report_repo = ReportRepository()
run_manager = RunManager(run_repo=run_repo)
report_validator = ReportValidationService()
run_lifecycle = RunLifecycleService(
    run_manager=run_manager,
    run_repo=run_repo,
    request_repo=request_repo,
    report_repo=report_repo,
    report_validator=report_validator,
)
ai_revenue_workflow = AIRevenueWorkflowService(
    request_repo=request_repo,
    run_repo=run_repo,
    run_manager=run_manager,
)
digital_audit_workflow = DigitalAuditWorkflowService(
    request_repo=request_repo,
    run_repo=run_repo,
    run_manager=run_manager,
    report_validator=report_validator,
)
