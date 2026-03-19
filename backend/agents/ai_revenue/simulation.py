from __future__ import annotations

from dataclasses import dataclass

from backend.schemas.ai_revenue import EstimatedRevenueGain, OptimizationAction, RevenueCurrentState


@dataclass(frozen=True, slots=True)
class SimulationOutput:
    estimated_revenue_gain: EstimatedRevenueGain


class SimulationAgent:
    """
    Deterministic impact model: bounded heuristic uplift by action priority.
    The objective is explainability over precision.
    """

    def run(
        self,
        current_state: RevenueCurrentState,
        optimization_actions: list[OptimizationAction],
    ) -> SimulationOutput:
        base = current_state.estimated_monthly_revenue
        weighted_uplift = 0.0
        assumptions = [
            "Uplift is estimated from deterministic weights by action priority.",
            "Revenue impact assumes stable traffic quality during execution.",
            "No external seasonality effects are included in V1 simulation.",
        ]

        for action in optimization_actions:
            if action.priority == "P1":
                weighted_uplift += 0.06
            elif action.priority == "P2":
                weighted_uplift += 0.035
            else:
                weighted_uplift += 0.02

        bounded_uplift = min(0.28, weighted_uplift)
        likely_gain = round(base * bounded_uplift, 2)
        conservative_gain = round(likely_gain * 0.6, 2)
        optimistic_gain = round(likely_gain * 1.35, 2)

        return SimulationOutput(
            estimated_revenue_gain=EstimatedRevenueGain(
                conservative_monthly_gain=conservative_gain,
                likely_monthly_gain=likely_gain,
                optimistic_monthly_gain=optimistic_gain,
                confidence_note=(
                    "Simulation uses bounded deterministic heuristics; values are directional ranges, "
                    "not probabilistic forecasts."
                ),
                assumptions=assumptions,
            )
        )
