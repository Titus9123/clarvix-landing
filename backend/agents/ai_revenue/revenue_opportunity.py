from pydantic import BaseModel, Field

from backend.agents.ai_revenue.website_analyzer import WebsiteAnalyzerOutput
from backend.tools.internal_metrics import InternalMetricsResponse


class RevenueIssueCandidate(BaseModel):
    issue: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list, max_length=10)


class RevenueOpportunityCandidate(BaseModel):
    opportunity: str
    expected_effect: str
    effort: str
    confidence: float = Field(ge=0.0, le=1.0)


class RevenueOpportunityOutput(BaseModel):
    revenue_issues: list[RevenueIssueCandidate]
    opportunities: list[RevenueOpportunityCandidate]


class RevenueOpportunityAgent:
    def run(
        self,
        analyzer_output: WebsiteAnalyzerOutput,
        business_description: str,
        revenue_model: str,
        main_concern: str,
        metrics: InternalMetricsResponse,
    ) -> RevenueOpportunityOutput:
        desc = business_description.lower()
        model = revenue_model.lower()
        concern = main_concern.lower()
        cta_score = analyzer_output.cta_presence.get("cta_visibility_score", 0.0)
        dropoff_risk = metrics.conversion_signals.get("checkout_dropoff_risk", 0.0)

        issues: list[RevenueIssueCandidate] = []
        opportunities: list[RevenueOpportunityCandidate] = []

        if cta_score < 0.5:
            issues.append(
                RevenueIssueCandidate(
                    issue="Primary monetization CTA likely underperforming",
                    confidence=round(0.55 + (0.5 - cta_score), 2),
                    evidence=[
                        analyzer_output.page_structure_summary,
                        "CTA visibility score below target threshold",
                    ],
                )
            )
            opportunities.append(
                RevenueOpportunityCandidate(
                    opportunity="Reposition and simplify primary CTA blocks on high-traffic pages",
                    expected_effect="Higher click-through to conversion intent pages",
                    effort="medium",
                    confidence=0.78,
                )
            )

        if dropoff_risk > 0.6:
            issues.append(
                RevenueIssueCandidate(
                    issue="Conversion path friction likely causing revenue leakage",
                    confidence=round(0.6 + (dropoff_risk - 0.6), 2),
                    evidence=[
                        f"Dropoff risk signal={dropoff_risk:.2f}",
                        "UX hints indicate conversion friction",
                    ],
                )
            )
            opportunities.append(
                RevenueOpportunityCandidate(
                    opportunity="Reduce form/checkout steps and remove non-essential fields",
                    expected_effect="Lower abandonment and improved conversion completion",
                    effort="medium",
                    confidence=0.74,
                )
            )

        if "subscription" in model or "retainer" in model:
            opportunities.append(
                RevenueOpportunityCandidate(
                    opportunity="Introduce renewal and expansion triggers for recurring clients",
                    expected_effect="Increase recurring revenue retention and upsell rate",
                    effort="low",
                    confidence=0.69,
                )
            )

        if "lead" in concern or "prospect" in concern or "pipeline" in concern:
            opportunities.append(
                RevenueOpportunityCandidate(
                    opportunity="Align landing messaging with intent-based segmented offers",
                    expected_effect="More qualified inbound leads and better close rate",
                    effort="medium",
                    confidence=0.71,
                )
            )

        if "b2b" in desc and "pricing" not in desc:
            issues.append(
                RevenueIssueCandidate(
                    issue="Pricing transparency may be insufficient for B2B qualification",
                    confidence=0.64,
                    evidence=["Business description indicates B2B context without clear pricing cues"],
                )
            )

        if not issues:
            issues.append(
                RevenueIssueCandidate(
                    issue="No critical leakage signal, but monetization clarity can be improved",
                    confidence=0.58,
                    evidence=["Signals are mixed; improvement opportunity remains"],
                )
            )

        if not opportunities:
            opportunities.append(
                RevenueOpportunityCandidate(
                    opportunity="Run controlled CTA and offer-position tests on top-entry pages",
                    expected_effect="Identify highest-converting monetization path quickly",
                    effort="low",
                    confidence=0.66,
                )
            )

        return RevenueOpportunityOutput(revenue_issues=issues, opportunities=opportunities)
