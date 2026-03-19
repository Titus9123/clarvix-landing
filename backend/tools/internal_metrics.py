import hashlib
import json
from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import urlopen

from pydantic import BaseModel, Field, HttpUrl


class InternalMetricsRequest(BaseModel):
    website_url: HttpUrl


class InternalMetricsResponse(BaseModel):
    traffic_estimate: int = Field(ge=0)
    conversion_signals: dict[str, float]
    engagement_signals: dict[str, float]


def build_mock_metrics(website_url: str) -> InternalMetricsResponse:
    seed = int(hashlib.sha256(website_url.encode("utf-8")).hexdigest()[:8], 16)

    traffic_estimate = 1500 + (seed % 8500)
    cta_visibility = round(((seed >> 3) % 100) / 100, 2)
    checkout_dropoff = round(((seed >> 6) % 100) / 100, 2)
    bounce_hint = round(((seed >> 9) % 100) / 100, 2)
    avg_session_depth = round((((seed >> 12) % 50) / 10), 2)

    return InternalMetricsResponse(
        traffic_estimate=traffic_estimate,
        conversion_signals={
            "cta_visibility_score": cta_visibility,
            "checkout_dropoff_risk": checkout_dropoff,
        },
        engagement_signals={
            "bounce_risk_hint": bounce_hint,
            "avg_session_depth_hint": avg_session_depth,
        },
    )


@dataclass(slots=True)
class InternalMetricsClient:
    base_url: str

    def fetch(self, website_url: str) -> InternalMetricsResponse:
        encoded_url = quote(website_url, safe="")
        endpoint = f"{self.base_url.rstrip('/')}/internal/metrics?website_url={encoded_url}"
        with urlopen(endpoint, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return InternalMetricsResponse(**payload)
