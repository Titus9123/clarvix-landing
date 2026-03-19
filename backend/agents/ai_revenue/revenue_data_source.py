from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from backend.db.repositories import ReportRepository
from backend.schemas.common import ServiceRequestOut, ServiceType
from backend.tools.internal_metrics import build_mock_metrics


@dataclass(frozen=True, slots=True)
class RevenueDataSnapshot:
    traffic_metrics: dict[str, float]
    conversion_metrics: dict[str, float]
    funnel_signals: dict[str, float]
    audit_signals: dict[str, float | bool]


class RevenueDataSource(Protocol):
    def get_traffic_metrics(self, request: ServiceRequestOut) -> dict[str, float]:
        ...

    def get_conversion_metrics(self, request: ServiceRequestOut) -> dict[str, float]:
        ...

    def get_funnel_signals(self, request: ServiceRequestOut) -> dict[str, float]:
        ...

    def get_audit_signals(self, request: ServiceRequestOut) -> dict[str, float | bool]:
        ...

    def get_snapshot(self, request: ServiceRequestOut) -> RevenueDataSnapshot:
        ...


class DeterministicRevenueDataSource:
    """
    V1 in-process data adapter that simulates an MCP-like source.
    No external I/O and no randomness.
    """

    def __init__(self, report_repo: ReportRepository) -> None:
        self.report_repo = report_repo

    def _metrics(self, request: ServiceRequestOut):
        if not request.website_url:
            raise ValueError("website_url is required for deterministic revenue data source")
        return build_mock_metrics(request.website_url)

    def _latest_digital_audit_report(self, request: ServiceRequestOut) -> dict:
        reports = self.report_repo.list()
        matching = [
            report
            for report in reports
            if report.request_id == request.id and report.service_type == ServiceType.DIGITAL_AUDIT
        ]
        if not matching:
            return {}
        latest = sorted(matching, key=lambda r: r.created_at, reverse=True)[0]
        return latest.report_json

    def get_traffic_metrics(self, request: ServiceRequestOut) -> dict[str, float]:
        metrics = self._metrics(request)
        traffic_estimate = float(metrics.traffic_estimate)
        traffic_capacity_floor = 2500.0
        return {
            "traffic_estimate": traffic_estimate,
            "traffic_capacity_floor": traffic_capacity_floor,
            "traffic_capacity_gap": max(0.0, traffic_capacity_floor - traffic_estimate),
        }

    def get_conversion_metrics(self, request: ServiceRequestOut) -> dict[str, float]:
        metrics = self._metrics(request)
        cta_visibility = float(metrics.conversion_signals.get("cta_visibility_score", 0.0))
        dropoff_risk = float(metrics.conversion_signals.get("checkout_dropoff_risk", 0.0))

        # Deterministic conversions approximation.
        observed_conversion_rate = max(0.01, min(0.25, (cta_visibility * 0.22) - (dropoff_risk * 0.14) + 0.07))
        baseline_conversion_rate = max(0.04, min(0.22, observed_conversion_rate + 0.035))
        return {
            "cta_visibility_score": cta_visibility,
            "checkout_dropoff_risk": dropoff_risk,
            "observed_conversion_rate": round(observed_conversion_rate, 4),
            "baseline_conversion_rate": round(baseline_conversion_rate, 4),
        }

    def get_funnel_signals(self, request: ServiceRequestOut) -> dict[str, float]:
        metrics = self._metrics(request)
        bounce_risk = float(metrics.engagement_signals.get("bounce_risk_hint", 0.0))
        session_depth = float(metrics.engagement_signals.get("avg_session_depth_hint", 0.0))

        tracking_coverage = max(0.1, min(1.0, 1.0 - (bounce_risk * 0.55)))
        funnel_integrity = max(0.1, min(1.0, (session_depth / 4.0) - (bounce_risk * 0.2)))
        return {
            "bounce_risk_hint": bounce_risk,
            "avg_session_depth_hint": session_depth,
            "tracking_coverage_score": round(tracking_coverage, 4),
            "funnel_integrity_score": round(funnel_integrity, 4),
        }

    def get_audit_signals(self, request: ServiceRequestOut) -> dict[str, float | bool]:
        report_json = self._latest_digital_audit_report(request)
        if not report_json:
            return {
                "audit_available": False,
                "overall_score": 0.0,
                "tracking_section_score": 0.0,
                "has_missing_tracking_events": False,
                "has_broken_funnels": False,
            }

        scoring = report_json.get("scoring", {})
        section_scores = scoring.get("section_scores", {})
        tracking_analysis = report_json.get("tracking_analysis", {})
        missing_events = tracking_analysis.get("missing_tracking_events", [])
        broken_funnels = tracking_analysis.get("broken_funnels", [])

        return {
            "audit_available": True,
            "overall_score": float(scoring.get("overall_score", 0.0)),
            "tracking_section_score": float(section_scores.get("tracking", 0.0)),
            "has_missing_tracking_events": bool(missing_events),
            "has_broken_funnels": bool(broken_funnels),
        }

    def get_snapshot(self, request: ServiceRequestOut) -> RevenueDataSnapshot:
        return RevenueDataSnapshot(
            traffic_metrics=self.get_traffic_metrics(request),
            conversion_metrics=self.get_conversion_metrics(request),
            funnel_signals=self.get_funnel_signals(request),
            audit_signals=self.get_audit_signals(request),
        )
