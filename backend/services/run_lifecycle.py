import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from backend.core.errors import AppError
from backend.db.database import get_connection
from backend.db.repositories import ReportRepository, ServiceRequestRepository, WorkflowRunRepository
from backend.schemas.common import ReportCreate, RequestStatus, RunStatus, ServiceType, WorkflowRunOut
from backend.services.report_validation import ReportValidationService
from backend.services.run_manager import RunManager


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunLifecycleService:
    def __init__(
        self,
        run_manager: RunManager,
        run_repo: WorkflowRunRepository,
        request_repo: ServiceRequestRepository,
        report_repo: ReportRepository,
        report_validator: ReportValidationService,
    ) -> None:
        self.run_manager = run_manager
        self.run_repo = run_repo
        self.request_repo = request_repo
        self.report_repo = report_repo
        self.report_validator = report_validator

    def transition(
        self,
        run_id: UUID,
        target_status: RunStatus,
        run_output: dict,
        error_message: str | None = None,
    ) -> WorkflowRunOut:
        if target_status == RunStatus.APPROVED:
            return self._approve_atomic(run_id=run_id, run_output=run_output)

        updated = self.run_manager.transition(run_id, target_status, run_output, error_message)
        request_id = updated.request_id

        if target_status in {RunStatus.RUNNING, RunStatus.NEEDS_REVIEW}:
            self.request_repo.update_status(request_id, RequestStatus.IN_REVIEW)
            return updated

        if target_status == RunStatus.FAILED:
            self.request_repo.update_status(request_id, RequestStatus.FAILED)
            return updated

        return updated

    def _approve_atomic(self, run_id: UUID, run_output: dict) -> WorkflowRunOut:
        final_report = run_output.get("final_report", {}) if isinstance(run_output.get("final_report", {}), dict) else {}
        report_json = run_output.get("report_json", {}) or final_report.get("report_json", {})
        report_markdown = run_output.get("report_markdown", "") or final_report.get("report_markdown", "")
        if not report_markdown:
            raise AppError(
                "missing_report_markdown",
                "run_output.report_markdown is required to approve a run",
                422,
            )

        conn = get_connection()
        cur = conn.cursor()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = cur.execute(
                "SELECT id, request_id, service_type, run_status FROM workflow_runs WHERE id = ?",
                (str(run_id),),
            ).fetchone()
            if not row:
                raise AppError("run_not_found", f"Run {run_id} not found", 404)

            existing_report = cur.execute(
                "SELECT id FROM reports WHERE run_id = ?",
                (str(run_id),),
            ).fetchone()

            current_status = RunStatus(row["run_status"])
            if current_status == RunStatus.APPROVED and existing_report:
                # Safe no-op for repeated approval calls.
                conn.commit()
                return self.run_repo.get(run_id)

            if current_status != RunStatus.NEEDS_REVIEW:
                raise AppError(
                    "invalid_run_transition",
                    f"Transition {current_status.value} -> approved is not allowed",
                    409,
                )

            if existing_report:
                raise AppError(
                    "duplicate_report_for_run",
                    f"Report already exists for run {run_id}",
                    409,
                )

            validated_report_json = self.report_validator.validate(
                service_type=ServiceType(row["service_type"]),
                payload=report_json,
            )

            ts = now_iso()
            cur.execute(
                """
                UPDATE workflow_runs
                SET run_status = ?, run_output = ?, error_message = ?, finished_at = ?
                WHERE id = ?
                """,
                (
                    RunStatus.APPROVED.value,
                    json.dumps(run_output),
                    None,
                    ts,
                    str(run_id),
                ),
            )

            report_payload = ReportCreate(
                request_id=row["request_id"],
                run_id=row["id"],
                service_type=row["service_type"],
                report_json=validated_report_json,
                report_markdown=report_markdown,
                version=1,
            )

            cur.execute(
                """
                INSERT INTO reports (
                    id, request_id, run_id, service_type, report_json,
                    report_markdown, version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    str(report_payload.request_id),
                    str(report_payload.run_id),
                    report_payload.service_type.value,
                    json.dumps(report_payload.report_json),
                    report_payload.report_markdown,
                    report_payload.version,
                    ts,
                ),
            )
            cur.execute(
                "UPDATE service_requests SET status = ?, updated_at = ? WHERE id = ?",
                (RequestStatus.COMPLETED.value, ts, str(row["request_id"])),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return self.run_repo.get(run_id)
