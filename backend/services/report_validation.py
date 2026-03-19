from typing import Any

from pydantic import ValidationError

from backend.core.errors import AppError
from backend.schemas.ai_revenue import AIRevenueOperationalReportV2
from backend.schemas.common import ServiceType
from backend.schemas.digital_audit import DigitalAuditReportV1


class ReportValidationService:
    def __init__(self) -> None:
        self._validators = {
            ServiceType.AI_REVENUE_OPTIMIZATION: AIRevenueOperationalReportV2,
            ServiceType.DIGITAL_AUDIT: DigitalAuditReportV1,
        }

    def validate(self, service_type: ServiceType, payload: dict[str, Any]) -> dict[str, Any]:
        schema = self._validators.get(service_type)
        if not schema:
            raise AppError(
                "report_schema_not_supported",
                f"No report schema validator registered for service_type={service_type.value}",
                400,
            )
        try:
            return schema.model_validate(payload).model_dump(mode="json")
        except ValidationError as exc:
            raise AppError(
                "invalid_report_payload",
                f"Report payload failed schema validation: {exc.errors()}",
                422,
            ) from exc
