from __future__ import annotations

from dataclasses import dataclass

from backend.agents.ai_revenue.revenue_data_source import RevenueDataSnapshot
from backend.schemas.ai_revenue import RevenueCurrentState


@dataclass(frozen=True, slots=True)
class MonitoringOutput:
    current_state: RevenueCurrentState


class RevenueMonitoringAgent:
    def run(
        self,
        data_snapshot: RevenueDataSnapshot,
        primary_concern: str,
        average_order_value_hint: float,
    ) -> MonitoringOutput:
        traffic_estimate = int(data_snapshot.traffic_metrics["traffic_estimate"])
        observed_conversion_rate = float(data_snapshot.conversion_metrics["observed_conversion_rate"])
        baseline_conversion_rate = float(data_snapshot.conversion_metrics["baseline_conversion_rate"])

        observed_aov = max(25.0, average_order_value_hint)
        baseline_aov = round(observed_aov * 1.08, 2)
        estimated_monthly_revenue = round(traffic_estimate * observed_conversion_rate * observed_aov, 2)

        return MonitoringOutput(
            current_state=RevenueCurrentState(
                traffic_estimate=traffic_estimate,
                cta_visibility_score=float(data_snapshot.conversion_metrics["cta_visibility_score"]),
                checkout_dropoff_risk=float(data_snapshot.conversion_metrics["checkout_dropoff_risk"]),
                bounce_risk_hint=float(data_snapshot.funnel_signals["bounce_risk_hint"]),
                avg_session_depth_hint=float(data_snapshot.funnel_signals["avg_session_depth_hint"]),
                tracking_coverage_score=float(data_snapshot.funnel_signals["tracking_coverage_score"]),
                funnel_integrity_score=float(data_snapshot.funnel_signals["funnel_integrity_score"]),
                baseline_conversion_rate=baseline_conversion_rate,
                observed_conversion_rate=observed_conversion_rate,
                baseline_average_order_value=baseline_aov,
                observed_average_order_value=round(observed_aov, 2),
                estimated_monthly_revenue=estimated_monthly_revenue,
                primary_concern=primary_concern,
            )
        )
