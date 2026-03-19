from uuid import UUID

from fastapi import APIRouter

from backend.api.deps import ai_revenue_workflow, run_lifecycle, run_repo
from backend.schemas.common import RunStatus, RunTransition, WorkflowRunCreate, WorkflowRunOut


router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=WorkflowRunOut)
def create_run(payload: WorkflowRunCreate) -> WorkflowRunOut:
    return run_repo.create(payload)


@router.get("", response_model=list[WorkflowRunOut])
def list_runs() -> list[WorkflowRunOut]:
    return run_repo.list()


@router.get("/{run_id}", response_model=WorkflowRunOut)
def get_run(run_id: UUID) -> WorkflowRunOut:
    return run_repo.get(run_id)


@router.post("/{run_id}/transition", response_model=WorkflowRunOut)
def transition_run(run_id: UUID, payload: RunTransition) -> WorkflowRunOut:
    target = RunStatus(payload.target_status)
    return run_lifecycle.transition(
        run_id=run_id,
        target_status=target,
        run_output=payload.run_output,
        error_message=payload.error_message,
    )


@router.post("/execute/ai-revenue/{request_id}", response_model=WorkflowRunOut)
def execute_ai_revenue_workflow(request_id: UUID) -> WorkflowRunOut:
    return ai_revenue_workflow.execute_for_request(request_id)
