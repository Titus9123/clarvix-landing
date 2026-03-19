from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.schemas.common import RequestStatus, RunStatus, ServiceType


@dataclass(slots=True)
class ServiceRequestRecord:
    id: UUID
    service_type: ServiceType
    status: RequestStatus
    client_name: str
    website_url: str | None
    business_description: str
    revenue_model: str
    main_concern: str
    input_payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class WorkflowRunRecord:
    id: UUID
    request_id: UUID
    service_type: ServiceType
    run_status: RunStatus
    run_input: dict[str, Any]
    run_output: dict[str, Any]
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None


@dataclass(slots=True)
class ReportRecord:
    id: UUID
    request_id: UUID
    run_id: UUID
    service_type: ServiceType
    report_json: dict[str, Any]
    report_markdown: str
    version: int
    created_at: datetime
