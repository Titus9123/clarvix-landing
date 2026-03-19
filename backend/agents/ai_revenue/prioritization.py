from pydantic import BaseModel, Field

class GenericIssueCandidate(BaseModel):
    issue: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class GenericOpportunityCandidate(BaseModel):
    opportunity: str
    expected_effect: str
    effort: str
    confidence: float = Field(ge=0.0, le=1.0)


class PrioritizedIssue(GenericIssueCandidate):
    impact: str
    reasoning: str


class PrioritizedOpportunity(GenericOpportunityCandidate):
    pass


class PrioritizationOutput(BaseModel):
    top_issues: list[PrioritizedIssue]
    opportunities: list[PrioritizedOpportunity]


class PrioritizationAgent:
    def _impact_label(self, confidence: float, evidence_count: int) -> str:
        score = confidence + min(evidence_count, 3) * 0.08
        if score >= 0.95:
            return "high"
        if score >= 0.72:
            return "medium"
        return "low"

    def run(
        self,
        issues: list[GenericIssueCandidate],
        opportunities: list[GenericOpportunityCandidate],
    ) -> PrioritizationOutput:
        sorted_issues = sorted(issues, key=lambda i: i.confidence, reverse=True)
        ranked_issues: list[PrioritizedIssue] = []
        for candidate in sorted_issues[:10]:
            impact = self._impact_label(candidate.confidence, len(candidate.evidence))
            ranked_issues.append(
                PrioritizedIssue(
                    issue=candidate.issue,
                    impact=impact,
                    confidence=round(candidate.confidence, 2),
                    evidence=candidate.evidence,
                    reasoning=f"Assigned {impact} impact based on confidence and evidence depth.",
                )
            )

        sorted_opps = sorted(opportunities, key=lambda o: (o.effort != "low", -o.confidence))
        ranked_opps = [
            PrioritizedOpportunity(
                opportunity=o.opportunity,
                expected_effect=o.expected_effect,
                effort=o.effort,
                confidence=round(o.confidence, 2),
            )
            for o in sorted_opps[:10]
        ]

        return PrioritizationOutput(top_issues=ranked_issues, opportunities=ranked_opps)
