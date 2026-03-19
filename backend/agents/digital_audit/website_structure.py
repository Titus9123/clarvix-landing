from pydantic import BaseModel, Field


class WebsiteStructureOutput(BaseModel):
    navigation_clarity: int = Field(ge=0, le=100)
    page_hierarchy: int = Field(ge=0, le=100)
    cta_placement: int = Field(ge=0, le=100)
    mobile_desktop_structure: int = Field(ge=0, le=100)
    issues: list[str] = Field(min_length=1, max_length=10)


class WebsiteStructureAgent:
    def run(self, website_url: str) -> WebsiteStructureOutput:
        url_len = len(website_url)
        slash_count = website_url.count("/")
        query_count = website_url.count("?")
        hyphen_count = website_url.count("-")

        navigation_clarity = max(30, min(95, 88 - slash_count * 4 - query_count * 8))
        page_hierarchy = max(25, min(95, 86 - max(0, slash_count - 3) * 6 - hyphen_count * 2))
        cta_placement = max(35, min(95, 85 - (url_len % 13)))
        mobile_desktop_structure = max(40, min(95, 82 - query_count * 10 + (url_len % 5)))

        issues = [
            "Navigation path depth may hide conversion pages"
            if navigation_clarity < 70
            else "Navigation appears mostly clear for primary journeys",
            "CTA placement likely inconsistent across page templates"
            if cta_placement < 72
            else "CTA placement likely visible on core pages",
            "Mobile layout hierarchy may differ from desktop conversion flow"
            if mobile_desktop_structure < 70
            else "Mobile and desktop hierarchy likely aligned",
        ]

        return WebsiteStructureOutput(
            navigation_clarity=navigation_clarity,
            page_hierarchy=page_hierarchy,
            cta_placement=cta_placement,
            mobile_desktop_structure=mobile_desktop_structure,
            issues=issues,
        )
