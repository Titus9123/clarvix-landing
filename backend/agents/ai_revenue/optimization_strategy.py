from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from backend.agents.ai_revenue.revenue_opportunity import OpportunitySignal
from backend.schemas.ai_revenue import RevenueAnomaly, RevenueLeak


@dataclass(frozen=True, slots=True)
class StrategyDecision:
    strategy_code: str
    priority: str
    objective: str
    reason: str
    expected_impact: str
    owner: Literal["marketing", "sales", "product", "web", "analytics"]
    eta_days: int
    sources: list[str]


@dataclass(frozen=True, slots=True)
class StrategyOutput:
    decisions: list[StrategyDecision]


class OptimizationStrategyAgent:
    def run(
        self,
        anomalies: list[RevenueAnomaly],
        leaks: list[RevenueLeak],
        opportunities: list[OpportunitySignal],
    ) -> StrategyOutput:
        decisions: list[StrategyDecision] = []
        leak_map = {leak.leak_code: leak for leak in leaks}

        for anomaly in anomalies:
            if anomaly.anomaly_code == "conversion_drop":
                decisions.append(
                    StrategyDecision(
                        strategy_code="recover_conversion_core",
                        priority="P1",
                        objective="Recover baseline conversion efficiency",
                        reason="Conversion anomaly indicates direct revenue leakage from existing demand.",
                        expected_impact="Reduce checkout and CTA abandonment in high-intent sessions.",
                        owner="web",
                        eta_days=10,
                        sources=[anomaly.anomaly_code, "conv_drop_leak"],
                    )
                )
            elif anomaly.anomaly_code == "missing_tracking":
                decisions.append(
                    StrategyDecision(
                        strategy_code="restore_tracking_control",
                        priority="P1",
                        objective="Restore attribution and optimization control",
                        reason="Missing tracking prevents deterministic optimization loops.",
                        expected_impact="Improve decision quality and remove blind budget allocation.",
                        owner="analytics",
                        eta_days=7,
                        sources=[anomaly.anomaly_code, "attribution_blind_leak"],
                    )
                )
            elif anomaly.anomaly_code == "broken_funnel":
                decisions.append(
                    StrategyDecision(
                        strategy_code="repair_funnel_progression",
                        priority="P1",
                        objective="Repair funnel progression continuity",
                        reason="Broken funnel transitions remove users before monetization events.",
                        expected_impact="Increase completion rate from mid-funnel stages.",
                        owner="product",
                        eta_days=14,
                        sources=[anomaly.anomaly_code, "funnel_break_leak"],
                    )
                )
            elif anomaly.anomaly_code == "traffic_mismatch":
                decisions.append(
                    StrategyDecision(
                        strategy_code="stabilize_qualified_traffic",
                        priority="P2",
                        objective="Stabilize qualified traffic flow",
                        reason="Traffic floor mismatch limits the system's monetization throughput.",
                        expected_impact="Lift demand volume without degrading conversion quality.",
                        owner="marketing",
                        eta_days=12,
                        sources=[anomaly.anomaly_code, "traffic_supply_leak"],
                    )
                )

        if any(signal.signal_code == "recurring_expansion" for signal in opportunities):
            decisions.append(
                StrategyDecision(
                    strategy_code="expand_recurring_revenue",
                    priority="P3",
                    objective="Expand recurring account value",
                    reason="Recurring model allows deterministic expansion triggers after core leakage fixes.",
                    expected_impact="Improve retention and expansion revenue from existing base.",
                    owner="sales",
                    eta_days=21,
                    sources=["recurring_expansion"],
                )
            )

        if not decisions:
            fallback_loss = sum(leak.estimated_monthly_loss for leak in leak_map.values())
            decisions.append(
                StrategyDecision(
                    strategy_code="continuous_optimization_loop",
                    priority="P2",
                    objective="Sustain weekly optimization loop",
                    reason=f"Leakage estimate still indicates optimization headroom ({fallback_loss:.2f}).",
                    expected_impact="Generate incremental gains via controlled offer/funnel tests.",
                    owner="marketing",
                    eta_days=14,
                    sources=["latent_monetization_leak"],
                )
            )

        return StrategyOutput(decisions=decisions)
