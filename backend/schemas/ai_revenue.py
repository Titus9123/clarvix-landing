from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AIRevenueIssue(BaseModel):
    issue: str = Field(min_length=5, max_length=300)
    impact: Literal["high", "medium", "low"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list, max_length=10)
    reasoning: str = Field(min_length=10, max_length=500)


class AIRevenueOpportunity(BaseModel):
    opportunity: str = Field(min_length=5, max_length=300)
    expected_effect: str = Field(min_length=5, max_length=300)
    effort: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0.0, le=1.0)


class AIRevenueAction(BaseModel):
    priority: Literal["P1", "P2", "P3"]
    action: str = Field(min_length=5, max_length=300)
    owner: Literal["marketing", "sales", "product", "web"]
    timeline: str = Field(min_length=3, max_length=100)


class AIRevenueReview(BaseModel):
    status: Literal["needs_review", "approved"]
    reviewed_by: str | None = None
    review_notes: str | None = None


class AIRevenueReportV1(BaseModel):
    schema_version: Literal["ai_revenue_report_v1"] = "ai_revenue_report_v1"
    request_id: UUID
    summary: str = Field(min_length=10, max_length=1200)
    top_issues: list[AIRevenueIssue] = Field(min_length=1, max_length=15)
    opportunities: list[AIRevenueOpportunity] = Field(min_length=1, max_length=15)
    action_plan: list[AIRevenueAction] = Field(min_length=1, max_length=20)
    review: AIRevenueReview
