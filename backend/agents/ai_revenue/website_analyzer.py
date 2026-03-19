from urllib.parse import urlparse

from pydantic import BaseModel, Field

from backend.tools.internal_metrics import InternalMetricsResponse


class WebsiteAnalyzerOutput(BaseModel):
    page_structure_summary: str
    cta_presence: dict[str, float | bool]
    basic_ux_issues: list[str] = Field(default_factory=list, max_length=10)
    performance_hints: list[str] = Field(default_factory=list, max_length=10)
    signal_flags: list[str] = Field(default_factory=list, max_length=10)


class WebsiteAnalyzerAgent:
    def run(self, website_url: str, metrics: InternalMetricsResponse) -> WebsiteAnalyzerOutput:
        parsed = urlparse(website_url)
        path_depth = len([p for p in parsed.path.split("/") if p])
        cta_visibility = metrics.conversion_signals.get("cta_visibility_score", 0.0)
        checkout_dropoff = metrics.conversion_signals.get("checkout_dropoff_risk", 0.0)
        bounce_hint = metrics.engagement_signals.get("bounce_risk_hint", 0.0)
        session_depth = metrics.engagement_signals.get("avg_session_depth_hint", 0.0)

        ux_issues: list[str] = []
        performance_hints: list[str] = []
        flags: list[str] = []

        if cta_visibility < 0.45:
            ux_issues.append("Low CTA visibility on primary pages")
            flags.append("weak_cta_surface")
        if checkout_dropoff > 0.6:
            ux_issues.append("Possible high friction in conversion path")
            flags.append("conversion_friction_risk")
        if bounce_hint > 0.55:
            ux_issues.append("Landing engagement risk is elevated")
            flags.append("engagement_drop_risk")
        if session_depth < 1.8:
            ux_issues.append("Low session depth suggests weak content progression")
            flags.append("shallow_session_pattern")

        if metrics.traffic_estimate < 2500:
            performance_hints.append("Traffic volume is limited; prioritize conversion efficiency first")
        if path_depth > 3:
            performance_hints.append("Deep navigation paths may hide commercial CTAs")
        if checkout_dropoff > 0.7:
            performance_hints.append("Audit checkout/booking form friction immediately")

        summary = (
            f"Domain {parsed.netloc} shows CTA score {cta_visibility:.2f}, "
            f"dropoff risk {checkout_dropoff:.2f}, and engagement risk {bounce_hint:.2f}."
        )

        return WebsiteAnalyzerOutput(
            page_structure_summary=summary,
            cta_presence={
                "cta_visible": cta_visibility >= 0.45,
                "cta_visibility_score": round(cta_visibility, 2),
            },
            basic_ux_issues=ux_issues,
            performance_hints=performance_hints,
            signal_flags=flags,
        )
