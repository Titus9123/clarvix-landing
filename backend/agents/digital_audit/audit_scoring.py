from pydantic import BaseModel, Field

from backend.agents.digital_audit.performance import PerformanceOutput
from backend.agents.digital_audit.tracking_integrity import TrackingIntegrityOutput
from backend.agents.digital_audit.trust_signal import TrustSignalOutput
from backend.agents.digital_audit.website_structure import WebsiteStructureOutput


class PrioritizedIssueOutput(BaseModel):
    issue: str
    impact: str
    recommendation: str
    severity: str


class AuditScoringOutput(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    section_scores: dict[str, int]
    prioritized_issues: list[PrioritizedIssueOutput] = Field(min_length=1, max_length=30)


class AuditScoringAgent:
    def run(
        self,
        structure: WebsiteStructureOutput,
        tracking: TrackingIntegrityOutput,
        performance: PerformanceOutput,
        trust: TrustSignalOutput,
    ) -> AuditScoringOutput:
        structure_score = int(
            round(
                (
                    structure.navigation_clarity
                    + structure.page_hierarchy
                    + structure.cta_placement
                    + structure.mobile_desktop_structure
                )
                / 4
            )
        )
        tracking_score = tracking.tracking_score
        performance_score = performance.page_load_speed
        trust_score = trust.trust_score

        overall_score = int(
            round(
                structure_score * 0.28
                + tracking_score * 0.27
                + performance_score * 0.22
                + trust_score * 0.23
            )
        )

        issues: list[PrioritizedIssueOutput] = []
        if tracking_score < 70:
            issues.append(
                PrioritizedIssueOutput(
                    issue="Tracking coverage gaps reduce attribution confidence.",
                    impact="Revenue decisions can miss high-intent sources.",
                    recommendation="Implement required events and repair funnel instrumentation.",
                    severity="high",
                )
            )
        if performance_score < 72:
            issues.append(
                PrioritizedIssueOutput(
                    issue="Performance bottlenecks may cause conversion drop-off.",
                    impact="Slow pages reduce completion rate for key actions.",
                    recommendation="Optimize heavy assets and remove render-blocking resources.",
                    severity="high",
                )
            )
        if structure_score < 74:
            issues.append(
                PrioritizedIssueOutput(
                    issue="Site hierarchy and CTA flow are not fully conversion-oriented.",
                    impact="Visitors may fail to reach monetization actions quickly.",
                    recommendation="Simplify hierarchy and place primary CTA consistently above the fold.",
                    severity="medium",
                )
            )
        if trust_score < 75:
            issues.append(
                PrioritizedIssueOutput(
                    issue="Trust signals are incomplete in critical decision moments.",
                    impact="Lower credibility can reduce lead quality and close intent.",
                    recommendation="Strengthen testimonials, legal transparency, and visible contact channels.",
                    severity="medium",
                )
            )
        if not issues:
            issues.append(
                PrioritizedIssueOutput(
                    issue="No major blockers detected; optimization headroom still exists.",
                    impact="Incremental gains remain possible with structured improvements.",
                    recommendation="Run structured optimization sprints on CTA, speed, and tracking quality.",
                    severity="low",
                )
            )

        return AuditScoringOutput(
            overall_score=overall_score,
            section_scores={
                "structure": structure_score,
                "tracking": tracking_score,
                "performance": performance_score,
                "trust": trust_score,
            },
            prioritized_issues=issues,
        )
