from uuid import UUID

from pydantic import BaseModel

from backend.agents.digital_audit.audit_scoring import AuditScoringOutput
from backend.agents.digital_audit.performance import PerformanceOutput
from backend.agents.digital_audit.tracking_integrity import TrackingIntegrityOutput
from backend.agents.digital_audit.trust_signal import TrustSignalOutput
from backend.agents.digital_audit.website_structure import WebsiteStructureOutput
from backend.schemas.digital_audit import DigitalAuditReportV1
from backend.tools.scan_input_loader import ScanContext


class AuditReportStructuringOutput(BaseModel):
    report_json: dict
    report_markdown: str


class AuditReportStructuringAgent:
    def _build_findings(
        self,
        structure: WebsiteStructureOutput,
        tracking: TrackingIntegrityOutput,
        performance: PerformanceOutput,
        trust: TrustSignalOutput,
        scan_context: ScanContext,
    ) -> list[dict]:
        findings: list[dict] = []

        def add(
            title: str,
            priority: str,
            exists: str,
            missing: str,
            impact: str,
            fix: str,
            effort: str,
        ) -> None:
            findings.append(
                {
                    "number": f"#{len(findings) + 1:02d}",
                    "title": title,
                    "priority": priority,
                    "exists": exists,
                    "missing": missing,
                    "impact": impact,
                    "fix": fix,
                    "effort": effort,
                }
            )

        has_template = "FINDINGS" in scan_context.template_blocks
        has_raw = any(path.lower().endswith(".json") for path in scan_context.input_sources)

        add(
            "Tracking foundation is incomplete for reliable attribution",
            "CRITICAL",
            f"Detected GA4 status: {tracking.ga4_presence}; pixel status: {tracking.pixel_signals}.",
            f"Missing tracking events: {', '.join(tracking.missing_tracking_events)}.",
            "Marketing and conversion decisions operate with partial visibility, reducing optimization precision.",
            "Implement GA4/GTM event map for lead actions and enforce event QA before campaigns.",
            "Low — 1-2 days",
        )
        add(
            "Conversion path friction likely affects lead completion",
            "CRITICAL",
            f"CTA placement score: {structure.cta_placement}/100.",
            f"Detected funnel breakpoints: {', '.join(tracking.broken_funnels)}.",
            "Visitors may start intent journeys but fail to complete high-value actions.",
            "Reduce conversion steps, align CTA hierarchy, and map key pages to single-purpose CTAs.",
            "Medium — 2-4 days",
        )
        add(
            "Mobile and desktop structure consistency needs reinforcement",
            "IMPORTANT",
            f"Navigation clarity score: {structure.navigation_clarity}/100.",
            f"Mobile/Desktop structure score: {structure.mobile_desktop_structure}/100.",
            "Inconsistent structure increases drop-off risk in high-intent sessions.",
            "Standardize page hierarchy and ensure consistent CTA placement across templates.",
            "Medium — 2-3 days",
        )
        add(
            "Page performance bottlenecks are likely reducing conversion momentum",
            "IMPORTANT",
            f"Performance score: {performance.page_load_speed}/100.",
            f"Heavy assets detected: {', '.join(performance.heavy_assets)}.",
            "Slow first interactions reduce engagement quality and lower qualified lead capture rate.",
            "Optimize heavy assets and defer render-blocking resources on critical entry pages.",
            "Medium — 2-5 days",
        )
        add(
            "Trust and proof signals are not fully maximized",
            "IMPORTANT",
            f"Testimonials status: {trust.testimonials_presence}; legal pages: {trust.legal_pages}.",
            "Trust signals are partial in some conversion-critical moments.",
            "Lower credibility at decision points can reduce contact initiation and close intent.",
            "Strengthen testimonial visibility, legal transparency, and contact trust anchors.",
            "Low — 1-2 days",
        )
        add(
            "Audit evidence framework exists and should be operationalized",
            "RECOMMENDED",
            f"Template blocks detected: {', '.join(scan_context.template_blocks) if scan_context.template_blocks else 'none'}.",
            f"Raw evidence files detected: {len(scan_context.evidence_files)}.",
            "Without structured reuse of evidence assets, recurring audits lose efficiency and consistency.",
            "Standardize evidence-to-report mapping using existing template sections and raw audit assets.",
            "Low — 1 day",
        )
        add(
            "Benchmark assets can support stronger market-position recommendations",
            "RECOMMENDED",
            f"Sections present from scan assets: {', '.join(scan_context.sections_present) if scan_context.sections_present else 'none'}.",
            "Benchmark context is available but not always reflected in visible recommendations.",
            "Missing benchmark context weakens urgency and competitive differentiation in client plans.",
            "Include competitor/market references in issue framing and in next-step actions.",
            "Low — 1 day",
        )
        add(
            "Report reproducibility controls are available and should remain mandatory",
            "RECOMMENDED",
            f"Template findings hint: {scan_context.findings_count_hint}; template detected: {has_template}.",
            f"Raw sample detected: {has_raw}.",
            "If reproducibility controls are bypassed, output quality drifts and operational trust decreases.",
            "Keep deterministic scoring and fixed report structure as non-optional generation constraints.",
            "Low — ongoing governance",
        )

        return findings[:10]

    def _build_action_plan(self, findings: list[dict]) -> list[dict]:
        mapping = {"CRITICAL": "CRITICAL", "IMPORTANT": "RECOMMENDED", "RECOMMENDED": "OPTIONAL"}
        day_ranges = {
            "CRITICAL": ["1-2", "2-3", "3-5", "5-7"],
            "RECOMMENDED": ["7-10", "10-14", "14-21"],
            "OPTIONAL": ["14-21", "21-30"],
        }
        counters = {"CRITICAL": 0, "RECOMMENDED": 0, "OPTIONAL": 0}
        plan: list[dict] = []

        for finding in findings:
            p = mapping[finding["priority"]]
            idx = min(counters[p], len(day_ranges[p]) - 1)
            counters[p] += 1
            owner = "Developer" if any(k in finding["title"].lower() for k in ["tracking", "performance", "structure"]) else "Audit Lead"
            plan.append(
                {
                    "priority": p,
                    "action": finding["title"],
                    "days": day_ranges[p][idx],
                    "owner": owner,
                }
            )
        return plan

    def run(
        self,
        request_id: UUID,
        website_url: str,
        business_description: str,
        main_concern: str,
        structure: WebsiteStructureOutput,
        tracking: TrackingIntegrityOutput,
        performance: PerformanceOutput,
        trust: TrustSignalOutput,
        scoring: AuditScoringOutput,
        scan_context: ScanContext,
    ) -> AuditReportStructuringOutput:
        findings = self._build_findings(
            structure=structure,
            tracking=tracking,
            performance=performance,
            trust=trust,
            scan_context=scan_context,
        )
        action_plan = self._build_action_plan(findings)

        report = DigitalAuditReportV1(
            request_id=request_id,
            site_overview={
                "website_url": website_url,
                "business_description": business_description,
                "main_concern": main_concern,
            },
            structure_analysis={
                "navigation_clarity": structure.navigation_clarity,
                "page_hierarchy": structure.page_hierarchy,
                "cta_placement": structure.cta_placement,
                "mobile_desktop_structure": structure.mobile_desktop_structure,
            },
            tracking_analysis={
                "ga4_presence": tracking.ga4_presence,
                "pixel_signals": tracking.pixel_signals,
                "missing_tracking_events": tracking.missing_tracking_events,
                "broken_funnels": tracking.broken_funnels,
            },
            performance_analysis={
                "page_load_speed": performance.page_load_speed,
                "heavy_assets": performance.heavy_assets,
                "render_blocking_issues": performance.render_blocking_issues,
            },
            trust_analysis={
                "testimonials_presence": trust.testimonials_presence,
                "contact_info_visibility": trust.contact_info_visibility,
                "legal_pages": trust.legal_pages,
                "brand_credibility_signals": trust.brand_credibility_signals,
            },
            scoring={
                "overall_score": scoring.overall_score,
                "section_scores": scoring.section_scores,
            },
            prioritized_issues=[
                {
                    "issue": i.issue,
                    "impact": i.impact,
                    "recommendation": i.recommendation,
                    "severity": i.severity,
                }
                for i in scoring.prioritized_issues
            ],
            findings=findings,
            action_plan=action_plan,
        )

        markdown = self._to_markdown(report)
        return AuditReportStructuringOutput(
            report_json=report.model_dump(mode="json"),
            report_markdown=markdown,
        )

    def _to_markdown(self, report: DigitalAuditReportV1) -> str:
        section_scores = report.scoring.section_scores
        issue_lines = "\n".join(
            [
                f"- [{issue.severity.upper()}] {issue.issue} -> {issue.recommendation}"
                for issue in report.prioritized_issues
            ]
        )
        finding_lines = "\n".join(
            [f"- {item.number} [{item.priority}] {item.title}" for item in report.findings]
        )
        plan_lines = "\n".join(
            [f"- {item.priority}: {item.action} ({item.days}, {item.owner})" for item in report.action_plan]
        )
        return (
            "# Digital Presence Audit\n\n"
            "## Site Overview\n"
            f"- URL: {report.site_overview.website_url}\n"
            f"- Main Concern: {report.site_overview.main_concern}\n\n"
            "## Scoring\n"
            f"- Overall: {report.scoring.overall_score}\n"
            f"- Structure: {section_scores.structure}\n"
            f"- Tracking: {section_scores.tracking}\n"
            f"- Performance: {section_scores.performance}\n"
            f"- Trust: {section_scores.trust}\n\n"
            "## Prioritized Issues\n"
            f"{issue_lines}\n\n"
            "## Findings\n"
            f"{finding_lines}\n\n"
            "## Action Plan\n"
            f"{plan_lines}\n"
        )
