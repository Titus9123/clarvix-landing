from uuid import UUID

from backend.core.errors import AppError
from backend.db.repositories import WorkflowRunRepository
from backend.schemas.common import RunStatus, WorkflowRunOut


ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.QUEUED: {RunStatus.RUNNING, RunStatus.FAILED},
    RunStatus.RUNNING: {RunStatus.NEEDS_REVIEW, RunStatus.FAILED},
    RunStatus.NEEDS_REVIEW: {RunStatus.APPROVED, RunStatus.FAILED},
    RunStatus.APPROVED: set(),
    RunStatus.FAILED: {RunStatus.QUEUED},
}


class RunManager:
    def __init__(self, run_repo: WorkflowRunRepository) -> None:
        self.run_repo = run_repo

    def transition(
        self,
        run_id: UUID,
        target_status: RunStatus,
        run_output: dict,
        error_message: str | None = None,
    ) -> WorkflowRunOut:
        current = self.run_repo.get(run_id)
        allowed = ALLOWED_TRANSITIONS[current.run_status]
        if target_status not in allowed:
            raise AppError(
                "invalid_run_transition",
                f"Transition {current.run_status.value} -> {target_status.value} is not allowed",
                409,
            )

        if target_status == RunStatus.FAILED and not error_message:
            raise AppError("error_message_required", "error_message is required when status=failed", 400)

        if target_status != RunStatus.FAILED:
            error_message = None

        return self.run_repo.update(
            run_id=run_id,
            run_status=target_status,
            run_output=run_output,
            error_message=error_message,
        )
