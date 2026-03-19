from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RevenueCurrentState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    traffic_estimate: int = Field(ge=0)
    cta_visibility_score: float = Field(ge=0.0, le=1.0)
    checkout_dropoff_risk: float = Field(ge=0.0, le=1.0)
    bounce_risk_hint: float = Field(ge=0.0, le=1.0)
    avg_session_depth_hint: float = Field(ge=0.0)
    tracking_coverage_score: float = Field(ge=0.0, le=1.0)
    funnel_integrity_score: float = Field(ge=0.0, le=1.0)
    baseline_conversion_rate: float = Field(ge=0.0, le=1.0)
    observed_conversion_rate: float = Field(ge=0.0, le=1.0)
    baseline_average_order_value: float = Field(ge=1.0)
    observed_average_order_value: float = Field(ge=1.0)
    estimated_monthly_revenue: float = Field(ge=0.0)
    primary_concern: str = Field(min_length=3, max_length=1000)


class RevenueAnomaly(BaseModel):
    model_config = ConfigDict(extra="forbid")
    anomaly_code: Literal[
        "conversion_drop",
        "traffic_mismatch",
        "missing_tracking",
        "broken_funnel",
    ]
    severity: Literal["high", "medium", "low"]
    metric: str = Field(min_length=3, max_length=80)
    observed_value: float = Field(ge=0.0)
    expected_value: float = Field(ge=0.0)
    delta: float
    reason: str = Field(min_length=10, max_length=500)


class RevenueLeak(BaseModel):
    model_config = ConfigDict(extra="forbid")
    leak_code: str = Field(min_length=4, max_length=120)
    description: str = Field(min_length=10, max_length=400)
    estimated_monthly_loss: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)
    linked_anomalies: list[str] = Field(default_factory=list, max_length=5)


class OptimizationAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: Literal["P1", "P2", "P3"]
    action: str = Field(min_length=5, max_length=300)
    reason: str = Field(min_length=10, max_length=500)
    expected_impact: str = Field(min_length=10, max_length=300)
    execution_steps: list[str] = Field(min_length=1, max_length=12)


class ExecutionPlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sequence: int = Field(ge=1, le=99)
    action: str = Field(min_length=5, max_length=300)
    priority: Literal["P1", "P2", "P3"]
    owner: Literal["marketing", "sales", "product", "web", "analytics"]
    eta_days: int = Field(ge=1, le=180)
    dependency: str | None = Field(default=None, max_length=300)


class EstimatedRevenueGain(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conservative_monthly_gain: float = Field(ge=0.0)
    likely_monthly_gain: float = Field(ge=0.0)
    optimistic_monthly_gain: float = Field(ge=0.0)
    confidence_note: str = Field(min_length=10, max_length=400)
    assumptions: list[str] = Field(min_length=1, max_length=10)


class AIRevenueReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["needs_review", "approved"]
    reviewed_by: str | None = None
    review_notes: str | None = None


class AIRevenueOperationalReportV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["ai_revenue_operational_v2"] = "ai_revenue_operational_v2"
    request_id: UUID
    current_state: RevenueCurrentState
    detected_anomalies: list[RevenueAnomaly] = Field(default_factory=list, max_length=20)
    revenue_leaks: list[RevenueLeak] = Field(default_factory=list, max_length=20)
    optimization_actions: list[OptimizationAction] = Field(min_length=1, max_length=30)
    execution_plan: list[ExecutionPlanItem] = Field(min_length=1, max_length=50)
    estimated_revenue_gain: EstimatedRevenueGain
    review: AIRevenueReview
