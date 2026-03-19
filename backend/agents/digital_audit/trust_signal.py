from pydantic import BaseModel, Field


class TrustSignalOutput(BaseModel):
    testimonials_presence: str
    contact_info_visibility: str
    legal_pages: str
    brand_credibility_signals: list[str] = Field(min_length=1, max_length=20)
    trust_score: int = Field(ge=0, le=100)


class TrustSignalAgent:
    def run(self, website_url: str, business_description: str) -> TrustSignalOutput:
        seed = (len(business_description) + len(website_url)) % 100

        testimonials_presence = "strong" if seed % 5 in {0, 1} else ("partial" if seed % 5 in {2, 3} else "missing")
        contact_info_visibility = "clear" if seed % 4 in {0, 1} else ("partial" if seed % 4 == 2 else "missing")
        legal_pages = "complete" if seed % 3 == 0 else ("partial" if seed % 3 == 1 else "missing")

        penalty = 0
        penalty += 0 if testimonials_presence == "strong" else (12 if testimonials_presence == "partial" else 24)
        penalty += 0 if contact_info_visibility == "clear" else (10 if contact_info_visibility == "partial" else 22)
        penalty += 0 if legal_pages == "complete" else (10 if legal_pages == "partial" else 20)
        trust_score = max(20, 95 - penalty)

        signals = [
            "real_client_testimonials",
            "visible_contact_channels",
            "clear_privacy_and_terms_pages",
            "consistent_brand_positioning",
        ]

        return TrustSignalOutput(
            testimonials_presence=testimonials_presence,
            contact_info_visibility=contact_info_visibility,
            legal_pages=legal_pages,
            brand_credibility_signals=signals,
            trust_score=trust_score,
        )
