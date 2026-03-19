from pydantic import BaseModel, Field


class TrackingIntegrityOutput(BaseModel):
    ga4_presence: str
    pixel_signals: str
    missing_tracking_events: list[str] = Field(min_length=1, max_length=20)
    broken_funnels: list[str] = Field(min_length=1, max_length=20)
    tracking_score: int = Field(ge=0, le=100)


class TrackingIntegrityAgent:
    def run(self, website_url: str) -> TrackingIntegrityOutput:
        seed = sum(ord(c) for c in website_url) % 100
        ga4_presence = "present" if seed % 3 != 0 else "missing"
        pixel_signals = "healthy" if seed % 4 == 0 else ("partial" if seed % 4 in {1, 2} else "missing")

        missing_events = [
            "form_submit",
            "cta_click_primary",
            "pricing_view",
            "checkout_start",
        ]
        broken_funnels = [
            "home_to_contact_funnel",
            "service_to_booking_funnel",
        ]

        penalty = 0
        penalty += 25 if ga4_presence == "missing" else 0
        penalty += 20 if pixel_signals == "missing" else (10 if pixel_signals == "partial" else 0)
        penalty += seed // 10
        tracking_score = max(20, 95 - penalty)

        return TrackingIntegrityOutput(
            ga4_presence=ga4_presence,
            pixel_signals=pixel_signals,
            missing_tracking_events=missing_events,
            broken_funnels=broken_funnels,
            tracking_score=tracking_score,
        )
