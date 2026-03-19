from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class LeadTargetFilters(BaseModel):
    industries: list[str] = Field(default_factory=list, max_length=20)
    roles: list[str] = Field(default_factory=list, max_length=20)
    geos: list[str] = Field(default_factory=list, max_length=20)
    min_company_size: int | None = Field(default=None, ge=1, le=1000000)
    max_company_size: int | None = Field(default=None, ge=1, le=1000000)
    require_verified_email: bool = True


class LeadTargetDefinition(BaseModel):
    industry: str = Field(min_length=2, max_length=120)
    roles: list[str] = Field(min_length=1, max_length=20)
    geos: list[str] = Field(min_length=1, max_length=20)
    filters: LeadTargetFilters = Field(default_factory=LeadTargetFilters)


class LeadRecord(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    company: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254)
    source: Literal["apollo"]
    icp_fit: Literal["high", "medium", "low"]
    notes: str = Field(default="", max_length=400)


class LeadBatchMetrics(BaseModel):
    total: int = Field(ge=0)
    high_fit: int = Field(ge=0)
    medium_fit: int = Field(ge=0)
    low_fit: int = Field(ge=0)


class LeadGenerationReview(BaseModel):
    status: Literal["needs_review", "approved"]
    reviewed_by: str | None = None
    review_notes: str | None = None


class LeadGenerationReportV1(BaseModel):
    schema_version: Literal["lead_generation_report_v1"] = "lead_generation_report_v1"
    request_id: UUID
    mode_used: Literal["apollo_api", "apollo_csv"]
    summary: str = Field(min_length=10, max_length=1000)
    target_definition: LeadTargetDefinition
    lead_batch: list[LeadRecord] = Field(default_factory=list, max_length=500)
    batch_metrics: LeadBatchMetrics
    next_actions: list[str] = Field(default_factory=list, max_length=20)
    review: LeadGenerationReview
