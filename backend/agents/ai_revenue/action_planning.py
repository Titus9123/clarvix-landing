from __future__ import annotations

from dataclasses import dataclass

from backend.agents.ai_revenue.optimization_strategy import StrategyDecision
from backend.schemas.ai_revenue import ExecutionPlanItem, OptimizationAction


@dataclass(frozen=True, slots=True)
class ActionPlanningOutput:
    optimization_actions: list[OptimizationAction]
    execution_plan: list[ExecutionPlanItem]


class ActionPlanningAgent:
    def _steps_for_strategy(self, decision: StrategyDecision) -> list[str]:
        if decision.strategy_code == "restore_tracking_control":
            return [
                "Audit missing events on conversion-critical pages.",
                "Implement deterministic event map for CTA, form start, form submit, and confirmation.",
                "Validate event continuity using internal QA checklist before rollout.",
            ]
        if decision.strategy_code == "repair_funnel_progression":
            return [
                "Trace funnel transitions and isolate highest-drop stage.",
                "Remove blocking UX elements and simplify progression path.",
                "Deploy corrected flow and verify stage-to-stage completion continuity.",
            ]
        if decision.strategy_code == "recover_conversion_core":
            return [
                "Reorder CTA hierarchy on top-entry pages by intent depth.",
                "Reduce non-essential checkout/form fields to minimum viable path.",
                "Run deterministic before/after conversion comparison over same traffic band.",
            ]
        if decision.strategy_code == "stabilize_qualified_traffic":
            return [
                "Shift spend and content emphasis toward channels with qualified session signatures.",
                "Apply message alignment between acquisition creatives and landing intent.",
                "Protect conversion efficiency thresholds while scaling traffic.",
            ]
        if decision.strategy_code == "expand_recurring_revenue":
            return [
                "Define expansion trigger events for active recurring accounts.",
                "Deploy renewal and upsell follow-up sequence tied to trigger events.",
                "Measure expansion conversion and retention impact by segment.",
            ]
        return [
            "Select one high-impact monetization lever from current state constraints.",
            "Execute a bounded optimization cycle with deterministic success criteria.",
            "Promote winning variant and retire underperforming variant.",
        ]

    def run(self, decisions: list[StrategyDecision]) -> ActionPlanningOutput:
        optimization_actions: list[OptimizationAction] = []
        execution_plan: list[ExecutionPlanItem] = []

        for index, decision in enumerate(decisions, start=1):
            steps = self._steps_for_strategy(decision)
            optimization_actions.append(
                OptimizationAction(
                    action=decision.objective,
                    reason=decision.reason,
                    expected_impact=decision.expected_impact,
                    priority=decision.priority,
                    execution_steps=steps,
                )
            )
            execution_plan.append(
                ExecutionPlanItem(
                    sequence=index,
                    action=decision.objective,
                    priority=decision.priority,
                    owner=decision.owner,
                    eta_days=decision.eta_days,
                    dependency=None if index == 1 else f"Complete sequence {index - 1}",
                )
            )

        return ActionPlanningOutput(
            optimization_actions=optimization_actions,
            execution_plan=execution_plan,
        )
