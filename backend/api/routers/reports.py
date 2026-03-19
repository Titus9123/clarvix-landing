from uuid import UUID

from fastapi import APIRouter

from backend.api.deps import report_repo, report_validator
from backend.schemas.common import ReportCreate, ReportOut


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportOut)
def create_report(payload: ReportCreate) -> ReportOut:
    validated_json = report_validator.validate(payload.service_type, payload.report_json)
    validated_payload = payload.model_copy(update={"report_json": validated_json})
    return report_repo.create(validated_payload)


@router.get("", response_model=list[ReportOut])
def list_reports() -> list[ReportOut]:
    return report_repo.list()


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: UUID) -> ReportOut:
    return report_repo.get(report_id)
