from dataclasses import dataclass

from backend.schemas.ai_revenue import RevenueAnomaly, RevenueCurrentState, RevenueLeak


@dataclass(frozen=True, slots=True)
class OpportunitySignal:
    signal_code: str
    description: str
    expected_effect: str
    effort: str
    confidence: float


@dataclass(frozen=True, slots=True)
class RevenueOpportunityOutput:
    revenue_leaks: list[RevenueLeak]
    opportunities: list[OpportunitySignal]


class RevenueOpportunityAgent:
    def run(
        self,
        anomalies: list[RevenueAnomaly],
        current_state: RevenueCurrentState,
        business_description: str,
        revenue_model: str,
        main_concern: str,
    ) -> RevenueOpportunityOutput:
        leaks: list[RevenueLeak] = []
        opportunities: list[OpportunitySignal] = []

        for anomaly in anomalies:
            if anomaly.anomaly_code == "conversion_drop":
                loss = max(0.0, current_state.estimated_monthly_revenue * 0.22)
                leaks.append(
                    RevenueLeak(
                        leak_code="conv_drop_leak",
                        description="Conversion efficiency is below baseline and leaking qualified demand.",
                        estimated_monthly_loss=round(loss, 2),
                        confidence=0.82,
                        linked_anomalies=[anomaly.anomaly_code],
                    )
                )
                opportunities.append(
                    OpportunitySignal(
                        signal_code="conversion_recovery",
                        description="Recover conversion rate by removing checkout and CTA friction.",
                        expected_effect="Higher conversion starts and completions from existing traffic.",
                        effort="medium",
                        confidence=0.8,
                    )
                )

            if anomaly.anomaly_code == "traffic_mismatch":
                loss = max(0.0, current_state.estimated_monthly_revenue * 0.15)
                leaks.append(
                    RevenueLeak(
                        leak_code="traffic_supply_leak",
                        description="Traffic volume below operational floor limits revenue throughput.",
                        estimated_monthly_loss=round(loss, 2),
                        confidence=0.74,
                        linked_anomalies=[anomaly.anomaly_code],
                    )
                )
                opportunities.append(
                    OpportunitySignal(
                        signal_code="traffic_quality_scaling",
                        description="Increase qualified traffic while protecting conversion efficiency.",
                        expected_effect="More conversion opportunities with controlled CPA pressure.",
                        effort="medium",
                        confidence=0.73,
                    )
                )

            if anomaly.anomaly_code == "missing_tracking":
                loss = max(0.0, current_state.estimated_monthly_revenue * 0.12)
                leaks.append(
                    RevenueLeak(
                        leak_code="attribution_blind_leak",
                        description="Missing tracking blocks optimization loops and hides revenue losses.",
                        estimated_monthly_loss=round(loss, 2),
                        confidence=0.79,
                        linked_anomalies=[anomaly.anomaly_code],
                    )
                )
                opportunities.append(
                    OpportunitySignal(
                        signal_code="tracking_restoration",
                        description="Restore full event tracking for monetization-critical steps.",
                        expected_effect="Reliable attribution and faster optimization cycles.",
                        effort="low",
                        confidence=0.85,
                    )
                )

            if anomaly.anomaly_code == "broken_funnel":
                loss = max(0.0, current_state.estimated_monthly_revenue * 0.18)
                leaks.append(
                    RevenueLeak(
                        leak_code="funnel_break_leak",
                        description="Broken funnel transitions are dropping users before revenue events.",
                        estimated_monthly_loss=round(loss, 2),
                        confidence=0.81,
                        linked_anomalies=[anomaly.anomaly_code],
                    )
                )
                opportunities.append(
                    OpportunitySignal(
                        signal_code="funnel_repair",
                        description="Repair broken progression steps from entry to conversion.",
                        expected_effect="Lower abandonment and improved purchase/lead completion.",
                        effort="high",
                        confidence=0.76,
                    )
                )

        desc = business_description.lower()
        model = revenue_model.lower()
        concern = main_concern.lower()

        if "subscription" in model or "retainer" in model:
            opportunities.append(
                OpportunitySignal(
                    signal_code="recurring_expansion",
                    description="Deploy expansion/renewal triggers for recurring revenue accounts.",
                    expected_effect="Higher retention and expansion MRR from existing customers.",
                    effort="low",
                    confidence=0.68,
                )
            )
        if "b2b" in desc and ("lead" in concern or "pipeline" in concern):
            opportunities.append(
                OpportunitySignal(
                    signal_code="qualification_acceleration",
                    description="Tighten B2B qualification and routing for high-intent leads.",
                    expected_effect="Faster sales velocity and lower lead-to-close leakage.",
                    effort="medium",
                    confidence=0.7,
                )
            )

        if not leaks:
            leaks.append(
                RevenueLeak(
                    leak_code="latent_monetization_leak",
                    description="No critical anomaly detected, but monetization path still has optimization headroom.",
                    estimated_monthly_loss=round(current_state.estimated_monthly_revenue * 0.06, 2),
                    confidence=0.58,
                    linked_anomalies=[],
                )
            )
        if not opportunities:
            opportunities.append(
                OpportunitySignal(
                    signal_code="iterative_offer_testing",
                    description="Run controlled offer and CTA iterations on top-entry pages.",
                    expected_effect="Incremental conversion uplift through deterministic weekly iterations.",
                    effort="low",
                    confidence=0.66,
                )
            )

        return RevenueOpportunityOutput(revenue_leaks=leaks, opportunities=opportunities)
