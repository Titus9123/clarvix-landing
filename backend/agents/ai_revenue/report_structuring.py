from uuid import UUID

from backend.schemas.ai_revenue import (
    AIRevenueOperationalReportV2,
    AIRevenueReview,
    EstimatedRevenueGain,
    ExecutionPlanItem,
    OptimizationAction,
    RevenueAnomaly,
    RevenueCurrentState,
    RevenueLeak,
)


class ReportStructuringAgent:
    def build_report(
        self,
        request_id: UUID,
        current_state: RevenueCurrentState,
        detected_anomalies: list[RevenueAnomaly],
        revenue_leaks: list[RevenueLeak],
        optimization_actions: list[OptimizationAction],
        execution_plan: list[ExecutionPlanItem],
        estimated_revenue_gain: EstimatedRevenueGain,
    ) -> AIRevenueOperationalReportV2:
        return AIRevenueOperationalReportV2(
            request_id=request_id,
            current_state=current_state,
            detected_anomalies=detected_anomalies,
            revenue_leaks=revenue_leaks,
            optimization_actions=optimization_actions,
            execution_plan=execution_plan,
            estimated_revenue_gain=estimated_revenue_gain,
            review=AIRevenueReview(status="needs_review"),
        )

    def build_markdown(self, report: AIRevenueOperationalReportV2) -> str:
        anomaly_lines = "\n".join(
            [
                (
                    f"- [{anomaly.severity.upper()}] {anomaly.anomaly_code} "
                    f"(metric={anomaly.metric}, observed={anomaly.observed_value:.4f}, "
                    f"expected={anomaly.expected_value:.4f}, delta={anomaly.delta:.4f})"
                )
                for anomaly in report.detected_anomalies
            ]
        ) or "- No critical anomalies detected in this deterministic cycle."
        leak_lines = "\n".join(
            [
                f"- {leak.leak_code}: {leak.description} (estimated_monthly_loss={leak.estimated_monthly_loss:.2f})"
                for leak in report.revenue_leaks
            ]
        ) or "- No explicit leaks detected."
        action_lines = "\n".join(
            [
                f"- {action.priority}: {action.action} -> {action.expected_impact}"
                for action in report.optimization_actions
            ]
        )
        plan_lines = "\n".join(
            [
                f"- Step {step.sequence}: [{step.priority}] {step.action} ({step.owner}, eta={step.eta_days}d)"
                for step in report.execution_plan
            ]
        )
        gain = report.estimated_revenue_gain

        return (
            "# Revenue Agent Operational Output\n\n"
            "## Current State\n"
            f"- estimated_monthly_revenue: {report.current_state.estimated_monthly_revenue:.2f}\n"
            f"- observed_conversion_rate: {report.current_state.observed_conversion_rate:.4f}\n"
            f"- baseline_conversion_rate: {report.current_state.baseline_conversion_rate:.4f}\n\n"
            f"## Detected Anomalies\n{anomaly_lines}\n\n"
            f"## Revenue Leaks\n{leak_lines}\n\n"
            f"## Optimization Actions\n{action_lines}\n\n"
            f"## Execution Plan\n{plan_lines}\n\n"
            "## Estimated Revenue Gain (Monthly)\n"
            f"- conservative: {gain.conservative_monthly_gain:.2f}\n"
            f"- likely: {gain.likely_monthly_gain:.2f}\n"
            f"- optimistic: {gain.optimistic_monthly_gain:.2f}\n\n"
            "## Review Status\n"
            f"- status: {report.review.status}\n"
        )
