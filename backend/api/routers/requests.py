from uuid import UUID

from fastapi import APIRouter

from backend.api.deps import request_repo
from backend.schemas.common import RequestStatusUpdate, ServiceRequestCreate, ServiceRequestOut


router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=ServiceRequestOut)
def create_request(payload: ServiceRequestCreate) -> ServiceRequestOut:
    return request_repo.create(payload)


@router.get("", response_model=list[ServiceRequestOut])
def list_requests() -> list[ServiceRequestOut]:
    return request_repo.list()


@router.get("/{request_id}", response_model=ServiceRequestOut)
def get_request(request_id: UUID) -> ServiceRequestOut:
    return request_repo.get(request_id)


@router.patch("/{request_id}/status", response_model=ServiceRequestOut)
def update_request_status(request_id: UUID, payload: RequestStatusUpdate) -> ServiceRequestOut:
    return request_repo.update_status(request_id, payload.status)
