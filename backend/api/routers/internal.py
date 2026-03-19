from fastapi import APIRouter, Query

from backend.tools.internal_metrics import InternalMetricsResponse, build_mock_metrics


router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/metrics", response_model=InternalMetricsResponse)
def get_internal_metrics(website_url: str = Query(min_length=8, max_length=2000)) -> InternalMetricsResponse:
    return build_mock_metrics(website_url)
