from __future__ import annotations

from dataclasses import dataclass

from backend.agents.ai_revenue.revenue_data_source import RevenueDataSnapshot
from backend.schemas.ai_revenue import RevenueAnomaly, RevenueCurrentState


@dataclass(frozen=True, slots=True)
class AnomalyDetectionOutput:
    anomalies: list[RevenueAnomaly]


class AnomalyDetectionAgent:
    def run(self, current_state: RevenueCurrentState, data_snapshot: RevenueDataSnapshot) -> AnomalyDetectionOutput:
        anomalies: list[RevenueAnomaly] = []

        conversion_gap = round(
            current_state.baseline_conversion_rate - current_state.observed_conversion_rate,
            4,
        )
        if conversion_gap > 0.015:
            severity = "high" if conversion_gap >= 0.045 else "medium"
            anomalies.append(
                RevenueAnomaly(
                    anomaly_code="conversion_drop",
                    severity=severity,
                    metric="conversion_rate",
                    observed_value=current_state.observed_conversion_rate,
                    expected_value=current_state.baseline_conversion_rate,
                    delta=round(current_state.observed_conversion_rate - current_state.baseline_conversion_rate, 4),
                    reason="Observed conversion rate is below deterministic baseline threshold.",
                )
            )

        traffic_gap = float(data_snapshot.traffic_metrics["traffic_capacity_gap"])
        traffic_floor = float(data_snapshot.traffic_metrics["traffic_capacity_floor"])
        if traffic_gap > 0:
            gap_ratio = traffic_gap / max(traffic_floor, 1.0)
            severity = "high" if gap_ratio >= 0.45 else "medium"
            anomalies.append(
                RevenueAnomaly(
                    anomaly_code="traffic_mismatch",
                    severity=severity,
                    metric="traffic_estimate",
                    observed_value=current_state.traffic_estimate,
                    expected_value=traffic_floor,
                    delta=round(current_state.traffic_estimate - traffic_floor, 2),
                    reason="Traffic volume is below deterministic minimum needed for monetization efficiency.",
                )
            )

        has_missing_tracking = bool(data_snapshot.audit_signals.get("has_missing_tracking_events", False))
        coverage = current_state.tracking_coverage_score
        if has_missing_tracking or coverage < 0.62:
            anomalies.append(
                RevenueAnomaly(
                    anomaly_code="missing_tracking",
                    severity="high" if coverage < 0.45 else "medium",
                    metric="tracking_coverage_score",
                    observed_value=coverage,
                    expected_value=0.75,
                    delta=round(coverage - 0.75, 4),
                    reason="Tracking coverage is insufficient to attribute drop-off and revenue outcomes reliably.",
                )
            )

        has_broken_funnels = bool(data_snapshot.audit_signals.get("has_broken_funnels", False))
        integrity = current_state.funnel_integrity_score
        if has_broken_funnels or integrity < 0.58:
            anomalies.append(
                RevenueAnomaly(
                    anomaly_code="broken_funnel",
                    severity="high" if integrity < 0.4 else "medium",
                    metric="funnel_integrity_score",
                    observed_value=integrity,
                    expected_value=0.7,
                    delta=round(integrity - 0.7, 4),
                    reason="Funnel progression integrity is weak and indicates broken or leaky conversion paths.",
                )
            )

        return AnomalyDetectionOutput(anomalies=anomalies)
