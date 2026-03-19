from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ScoreCategory(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    score: int = Field(ge=0, le=100)
    max_score: int = Field(default=100, ge=1, le=100)
    notes: str = Field(default="", max_length=400)


class ScoreOverview(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    categories: list[ScoreCategory] = Field(min_length=1, max_length=20)


class TopFinding(BaseModel):
    finding: str = Field(min_length=5, max_length=300)
    severity: Literal["high", "medium", "low"]
    evidence: list[str] = Field(default_factory=list, max_length=10)
    recommendation: str = Field(min_length=5, max_length=400)


class AuditAction(BaseModel):
    priority: Literal["P1", "P2", "P3"]
    action: str = Field(min_length=5, max_length=300)
    timeline: str = Field(min_length=3, max_length=100)


class DigitalAuditReview(BaseModel):
    status: Literal["needs_review", "approved"]
    reviewed_by: str | None = None
    review_notes: str | None = None


class DigitalAuditReportV1(BaseModel):
    schema_version: Literal["digital_audit_report_v1"] = "digital_audit_report_v1"
    request_id: UUID
    summary: str = Field(min_length=10, max_length=1200)
    score_overview: ScoreOverview
    top_findings: list[TopFinding] = Field(min_length=1, max_length=20)
    action_plan: list[AuditAction] = Field(min_length=1, max_length=20)
    review: DigitalAuditReview
