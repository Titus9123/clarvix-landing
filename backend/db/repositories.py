import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from backend.core.errors import AppError
from backend.db.database import get_connection
from backend.schemas.common import (
    ReportCreate,
    ReportOut,
    RequestStatus,
    RunStatus,
    ServiceRequestCreate,
    ServiceRequestOut,
    ServiceType,
    WorkflowRunCreate,
    WorkflowRunOut,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_service_request(row: dict) -> ServiceRequestOut:
    return ServiceRequestOut(
        id=UUID(row["id"]),
        service_type=ServiceType(row["service_type"]),
        status=RequestStatus(row["status"]),
        client_name=row["client_name"],
        website_url=row["website_url"],
        business_description=row["business_description"],
        revenue_model=row["revenue_model"],
        main_concern=row["main_concern"],
        input_payload=json.loads(row["input_payload"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _parse_workflow_run(row: dict) -> WorkflowRunOut:
    return WorkflowRunOut(
        id=UUID(row["id"]),
        request_id=UUID(row["request_id"]),
        service_type=ServiceType(row["service_type"]),
        run_status=RunStatus(row["run_status"]),
        run_input=json.loads(row["run_input"]),
        run_output=json.loads(row["run_output"]),
        error_message=row["error_message"],
        started_at=datetime.fromisoformat(row["started_at"]),
        finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
    )


def _parse_report(row: dict) -> ReportOut:
    return ReportOut(
        id=UUID(row["id"]),
        request_id=UUID(row["request_id"]),
        run_id=UUID(row["run_id"]),
        service_type=ServiceType(row["service_type"]),
        report_json=json.loads(row["report_json"]),
        report_markdown=row["report_markdown"],
        version=row["version"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


class ServiceRequestRepository:
    def create(self, data: ServiceRequestCreate) -> ServiceRequestOut:
        req_id = str(uuid4())
        ts = now_iso()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO service_requests (
                id, service_type, status, client_name, website_url,
                business_description, revenue_model, main_concern, input_payload,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                req_id,
                data.service_type.value,
                RequestStatus.NEW.value,
                data.client_name,
                str(data.website_url) if data.website_url else None,
                data.business_description,
                data.revenue_model,
                data.main_concern,
                json.dumps(data.input_payload),
                ts,
                ts,
            ),
        )
        conn.commit()
        conn.close()
        return self.get(UUID(req_id))

    def list(self) -> list[ServiceRequestOut]:
        conn = get_connection()
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT * FROM service_requests ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [_parse_service_request(dict(r)) for r in rows]

    def get(self, request_id: UUID) -> ServiceRequestOut:
        conn = get_connection()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT * FROM service_requests WHERE id = ?",
            (str(request_id),),
        ).fetchone()
        conn.close()
        if not row:
            raise AppError("request_not_found", f"Request {request_id} not found", 404)
        return _parse_service_request(dict(row))

    def update_status(self, request_id: UUID, status: RequestStatus) -> ServiceRequestOut:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE service_requests SET status = ?, updated_at = ? WHERE id = ?",
            (status.value, now_iso(), str(request_id)),
        )
        if cur.rowcount == 0:
            conn.close()
            raise AppError("request_not_found", f"Request {request_id} not found", 404)
        conn.commit()
        conn.close()
        return self.get(request_id)


class WorkflowRunRepository:
    def __init__(self, request_repo: ServiceRequestRepository) -> None:
        self.request_repo = request_repo

    def create(self, data: WorkflowRunCreate) -> WorkflowRunOut:
        request = self.request_repo.get(data.request_id)
        run_id = str(uuid4())
        ts = now_iso()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO workflow_runs (
                id, request_id, service_type, run_status, run_input, run_output,
                error_message, started_at, finished_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(data.request_id),
                request.service_type.value,
                RunStatus.QUEUED.value,
                json.dumps(data.run_input),
                json.dumps({}),
                None,
                ts,
                None,
            ),
        )
        conn.commit()
        conn.close()
        return self.get(UUID(run_id))

    def list(self) -> list[WorkflowRunOut]:
        conn = get_connection()
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT * FROM workflow_runs ORDER BY started_at DESC"
        ).fetchall()
        conn.close()
        return [_parse_workflow_run(dict(r)) for r in rows]

    def get(self, run_id: UUID) -> WorkflowRunOut:
        conn = get_connection()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT * FROM workflow_runs WHERE id = ?",
            (str(run_id),),
        ).fetchone()
        conn.close()
        if not row:
            raise AppError("run_not_found", f"Run {run_id} not found", 404)
        return _parse_workflow_run(dict(row))

    def update(
        self,
        run_id: UUID,
        run_status: RunStatus,
        run_output: dict,
        error_message: str | None,
    ) -> WorkflowRunOut:
        finished_at = now_iso() if run_status in {RunStatus.APPROVED, RunStatus.FAILED} else None
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE workflow_runs
            SET run_status = ?, run_output = ?, error_message = ?, finished_at = ?
            WHERE id = ?
            """,
            (run_status.value, json.dumps(run_output), error_message, finished_at, str(run_id)),
        )
        if cur.rowcount == 0:
            conn.close()
            raise AppError("run_not_found", f"Run {run_id} not found", 404)
        conn.commit()
        conn.close()
        return self.get(run_id)


class ReportRepository:
    def create(self, data: ReportCreate) -> ReportOut:
        report_id = str(uuid4())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO reports (
                id, request_id, run_id, service_type, report_json,
                report_markdown, version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                str(data.request_id),
                str(data.run_id),
                data.service_type.value,
                json.dumps(data.report_json),
                data.report_markdown,
                data.version,
                now_iso(),
            ),
        )
        conn.commit()
        conn.close()
        return self.get(UUID(report_id))

    def list(self) -> list[ReportOut]:
        conn = get_connection()
        cur = conn.cursor()
        rows = cur.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
        conn.close()
        return [_parse_report(dict(r)) for r in rows]

    def get(self, report_id: UUID) -> ReportOut:
        conn = get_connection()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT * FROM reports WHERE id = ?",
            (str(report_id),),
        ).fetchone()
        conn.close()
        if not row:
            raise AppError("report_not_found", f"Report {report_id} not found", 404)
        return _parse_report(dict(row))

    def get_by_run_id(self, run_id: UUID) -> ReportOut | None:
        conn = get_connection()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT * FROM reports WHERE run_id = ?",
            (str(run_id),),
        ).fetchone()
        conn.close()
        if not row:
            return None
        return _parse_report(dict(row))
