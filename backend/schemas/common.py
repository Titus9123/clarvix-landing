from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ServiceType(str, Enum):
    DIGITAL_AUDIT = "digital_audit"
    LEAD_GENERATION = "lead_generation"
    AI_REVENUE_OPTIMIZATION = "ai_revenue_optimization"


class RequestStatus(str, Enum):
    NEW = "new"
    IN_REVIEW = "in_review"
    READY_TO_RUN = "ready_to_run"
    COMPLETED = "completed"
    FAILED = "failed"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    FAILED = "failed"


class ServiceRequestCreate(BaseModel):
    service_type: ServiceType
    client_name: str = Field(min_length=2, max_length=120)
    website_url: HttpUrl | None = None
    business_description: str = Field(min_length=10, max_length=3000)
    revenue_model: str = Field(min_length=3, max_length=1000)
    main_concern: str = Field(min_length=3, max_length=1000)
    input_payload: dict[str, Any] = Field(default_factory=dict)


class ServiceRequestOut(BaseModel):
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


class RequestStatusUpdate(BaseModel):
    status: RequestStatus


class WorkflowRunCreate(BaseModel):
    request_id: UUID
    run_input: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunOut(BaseModel):
    id: UUID
    request_id: UUID
    service_type: ServiceType
    run_status: RunStatus
    run_input: dict[str, Any]
    run_output: dict[str, Any]
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None


class RunTransition(BaseModel):
    target_status: Literal["queued", "running", "needs_review", "approved", "failed"]
    run_output: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None


class ReportCreate(BaseModel):
    request_id: UUID
    run_id: UUID
    service_type: ServiceType
    report_json: dict[str, Any]
    report_markdown: str = Field(min_length=10)
    version: int = Field(ge=1, default=1)


class ReportOut(BaseModel):
    id: UUID
    request_id: UUID
    run_id: UUID
    service_type: ServiceType
    report_json: dict[str, Any]
    report_markdown: str
    version: int
    created_at: datetime
