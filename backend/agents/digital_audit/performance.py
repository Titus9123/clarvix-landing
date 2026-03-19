from pydantic import BaseModel, Field


class PerformanceOutput(BaseModel):
    page_load_speed: int = Field(ge=0, le=100)
    heavy_assets: list[str] = Field(min_length=1, max_length=20)
    render_blocking_issues: list[str] = Field(min_length=1, max_length=20)


class PerformanceAgent:
    def run(self, website_url: str) -> PerformanceOutput:
        length = len(website_url)
        dot_count = website_url.count(".")
        path_count = website_url.count("/")
        score = max(25, min(95, 90 - ((length % 17) + dot_count * 2 + max(0, path_count - 3) * 3)))

        heavy_assets = [
            "hero_video_large",
            "uncompressed_images_bundle",
            "blocking_webfont_chain",
        ]
        render_blocking_issues = [
            "critical_css_not_inlined",
            "sync_third_party_script_before_cta",
        ]

        return PerformanceOutput(
            page_load_speed=score,
            heavy_assets=heavy_assets,
            render_blocking_issues=render_blocking_issues,
        )
