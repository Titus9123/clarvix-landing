from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SiteOverview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    website_url: str = Field(min_length=8, max_length=2000)
    business_description: str = Field(min_length=10, max_length=3000)
    main_concern: str = Field(min_length=3, max_length=1000)


class StructureAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    navigation_clarity: int = Field(ge=0, le=100)
    page_hierarchy: int = Field(ge=0, le=100)
    cta_placement: int = Field(ge=0, le=100)
    mobile_desktop_structure: int = Field(ge=0, le=100)


class TrackingAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ga4_presence: Literal["present", "missing"]
    pixel_signals: Literal["healthy", "partial", "missing"]
    missing_tracking_events: list[str] = Field(min_length=1, max_length=20)
    broken_funnels: list[str] = Field(min_length=1, max_length=20)


class PerformanceAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page_load_speed: int = Field(ge=0, le=100)
    heavy_assets: list[str] = Field(min_length=1, max_length=20)
    render_blocking_issues: list[str] = Field(min_length=1, max_length=20)


class TrustAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    testimonials_presence: Literal["strong", "partial", "missing"]
    contact_info_visibility: Literal["clear", "partial", "missing"]
    legal_pages: Literal["complete", "partial", "missing"]
    brand_credibility_signals: list[str] = Field(min_length=1, max_length=20)


class SectionScores(BaseModel):
    model_config = ConfigDict(extra="forbid")
    structure: int = Field(ge=0, le=100)
    tracking: int = Field(ge=0, le=100)
    performance: int = Field(ge=0, le=100)
    trust: int = Field(ge=0, le=100)


class Scoring(BaseModel):
    model_config = ConfigDict(extra="forbid")
    overall_score: int = Field(ge=0, le=100)
    section_scores: SectionScores


class PrioritizedIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue: str = Field(min_length=5, max_length=300)
    impact: str = Field(min_length=5, max_length=200)
    recommendation: str = Field(min_length=5, max_length=400)
    severity: Literal["high", "medium", "low"]


class AuditFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    number: str = Field(pattern=r"^#\d{2}$")
    title: str = Field(min_length=5, max_length=240)
    priority: Literal["CRITICAL", "IMPORTANT", "RECOMMENDED"]
    exists: str = Field(min_length=5, max_length=1200)
    missing: str = Field(min_length=5, max_length=1500)
    impact: str = Field(min_length=5, max_length=1500)
    fix: str = Field(min_length=5, max_length=1500)
    effort: str = Field(min_length=3, max_length=180)


class ActionPlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: Literal["CRITICAL", "RECOMMENDED", "OPTIONAL"]
    action: str = Field(min_length=5, max_length=240)
    days: str = Field(min_length=1, max_length=32)
    owner: str = Field(min_length=2, max_length=80)


class DigitalAuditReportV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["digital_audit_report_v1"] = "digital_audit_report_v1"
    request_id: UUID
    site_overview: SiteOverview
    structure_analysis: StructureAnalysis
    tracking_analysis: TrackingAnalysis
    performance_analysis: PerformanceAnalysis
    trust_analysis: TrustAnalysis
    scoring: Scoring
    prioritized_issues: list[PrioritizedIssue] = Field(min_length=1, max_length=30)
    findings: list[AuditFinding] = Field(min_length=1, max_length=20)
    action_plan: list[ActionPlanItem] = Field(min_length=1, max_length=30)
