from uuid import UUID

from backend.agents.ai_revenue.prioritization import PrioritizationOutput
from backend.agents.ai_revenue.website_analyzer import WebsiteAnalyzerOutput
from backend.schemas.ai_revenue import (
    AIRevenueAction,
    AIRevenueOpportunity,
    AIRevenueReportV1,
    AIRevenueReview,
)


class ReportStructuringAgent:
    def build_report(
        self,
        request_id: UUID,
        analyzer_output: WebsiteAnalyzerOutput,
        prioritized: PrioritizationOutput,
        main_concern: str,
    ) -> AIRevenueReportV1:
        actions = [
            AIRevenueAction(
                priority="P1",
                action="Fix primary conversion friction and clarify CTA paths on top-entry pages",
                owner="web",
                timeline="7 days",
            ),
            AIRevenueAction(
                priority="P2",
                action="Align commercial messaging to concern-driven offer blocks",
                owner="marketing",
                timeline="14 days",
            ),
            AIRevenueAction(
                priority="P3",
                action="Track lead intent and post-click progression for optimization cycles",
                owner="sales",
                timeline="30 days",
            ),
        ]

        opportunities = [
            AIRevenueOpportunity(
                opportunity=o.opportunity,
                expected_effect=o.expected_effect,
                effort=o.effort,
                confidence=o.confidence,
            )
            for o in prioritized.opportunities
        ]

        summary = (
            "Revenue leakage signals were identified from site-level conversion and engagement hints. "
            f"Main concern considered: {main_concern}. "
            f"Analyzer summary: {analyzer_output.page_structure_summary}"
        )

        return AIRevenueReportV1(
            request_id=request_id,
            summary=summary,
            top_issues=[
                {
                    "issue": i.issue,
                    "impact": i.impact,
                    "confidence": i.confidence,
                    "evidence": i.evidence,
                    "reasoning": i.reasoning,
                }
                for i in prioritized.top_issues
            ],
            opportunities=opportunities,
            action_plan=actions,
            review=AIRevenueReview(status="needs_review"),
        )

    def build_markdown(self, report: AIRevenueReportV1) -> str:
        issue_lines = "\n".join(
            [
                f"- [{issue.impact.upper()} | conf={issue.confidence:.2f}] {issue.issue}"
                for issue in report.top_issues
            ]
        )
        opp_lines = "\n".join(
            [
                f"- ({opp.effort}) {opp.opportunity} -> {opp.expected_effect} [conf={opp.confidence:.2f}]"
                for opp in report.opportunities
            ]
        )
        action_lines = "\n".join(
            [f"- {a.priority}: {a.action} ({a.owner}, {a.timeline})" for a in report.action_plan]
        )

        return (
            "# AI Revenue Optimization Audit\n\n"
            f"## Summary\n{report.summary}\n\n"
            f"## Top Issues\n{issue_lines}\n\n"
            f"## Opportunities\n{opp_lines}\n\n"
            f"## Action Plan\n{action_lines}\n\n"
            "## Review Status\n"
            f"- status: {report.review.status}\n"
        )
