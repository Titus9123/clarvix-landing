from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from pydantic import BaseModel, Field


SCANS_DIR = Path(r"C:\Users\alber\OneDrive\Documentos\AntiGravity\Clarvix\Scans")


class ScanFileMeta(BaseModel):
    path: str
    file_type: str
    size_bytes: int
    modified_ts: float


class ScanContext(BaseModel):
    input_sources: list[str] = Field(default_factory=list)
    template_blocks: list[str] = Field(default_factory=list)
    sections_present: list[str] = Field(default_factory=list)
    findings_count_hint: int = Field(ge=0, default=0)
    sample_entities: list[str] = Field(default_factory=list)
    evidence_files: list[ScanFileMeta] = Field(default_factory=list)


@dataclass(slots=True)
class ScanInputLoader:
    scans_dir: Path = SCANS_DIR

    def _file_meta(self, path: Path) -> ScanFileMeta:
        stat = path.stat()
        return ScanFileMeta(
            path=str(path),
            file_type=path.suffix.lower(),
            size_bytes=stat.st_size,
            modified_ts=stat.st_mtime,
        )

    def _read_text_safe(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def _extract_template_blocks(self, template_text: str) -> list[str]:
        blocks = []
        for block in [
            "CLIENT",
            "COMPETITORS",
            "SCORE_BLOCKS",
            "FINDINGS",
            "PLAN_ITEMS",
            "BENCH_METRICS",
        ]:
            if re.search(rf"^\s*{re.escape(block)}\s*=", template_text, flags=re.MULTILINE):
                blocks.append(block)
        return blocks

    def _extract_findings_hint(self, template_text: str, audit_text: str) -> int:
        template_count = len(re.findall(r'\"num\"\s*:\s*\"#\d{2}\"', template_text))
        if template_count > 0:
            return template_count
        # fallback to narrative hints in scripts
        if "10 findings" in template_text.lower() or "10 findings" in audit_text.lower():
            return 10
        return 0

    def _extract_sections_present(self, audit_text: str) -> list[str]:
        mapping = {
            "tracking": ["tracking", "ga4", "gtm", "pixel"],
            "funnel": ["funnel", "form", "cta", "lead magnet"],
            "performance": ["pagespeed", "lcp", "tbt", "speed index"],
            "trust": ["testimonial", "privacy", "trust", "badge"],
            "seo": ["seo", "meta description", "sitemap", "robots.txt"],
            "local_presence": ["google maps", "gbp", "3-pack", "reviews"],
            "security": ["https", "safe browsing", "mixed content"],
            "competitors": ["competidor", "competitors", "benchmark"],
            "action_plan": ["30 días", "action plan", "plan"],
        }
        lower = audit_text.lower()
        sections: list[str] = []
        for section, keywords in mapping.items():
            if any(k.lower() in lower for k in keywords):
                sections.append(section)
        return sections

    def _extract_sample_entities(self, raw_json: dict) -> list[str]:
        entities: list[str] = []
        # deterministic and small extraction
        for key in ["business_name", "name", "city", "url"]:
            value = raw_json.get(key)
            if isinstance(value, str) and value.strip():
                entities.append(value.strip())
        for nested_key in ["site", "local"]:
            nested = raw_json.get(nested_key)
            if isinstance(nested, dict):
                for key in ["phone_number", "email_address", "maps_url"]:
                    value = nested.get(key)
                    if isinstance(value, str) and value.strip():
                        entities.append(value.strip())
        # preserve order and uniqueness
        deduped: list[str] = []
        for item in entities:
            if item not in deduped:
                deduped.append(item)
        return deduped[:20]

    def _extract_xlsx_metadata(self, xlsx_path: Path) -> list[str]:
        try:
            with ZipFile(xlsx_path, "r") as zf:
                workbook_xml = zf.read("xl/workbook.xml").decode("utf-8", errors="ignore")
            return re.findall(r'<sheet[^>]*name="([^"]+)"', workbook_xml)[:20]
        except Exception:
            return []

    def _extract_pdf_page_hint(self, pdf_path: Path) -> int:
        try:
            data = pdf_path.read_bytes()
            # heuristic: count page objects in PDF structure
            return max(1, len(re.findall(rb"/Type\s*/Page\b", data)))
        except Exception:
            return 0

    def build_context(self) -> ScanContext:
        if not self.scans_dir.exists():
            return ScanContext()

        py_files = sorted(self.scans_dir.glob("*.py"))
        pdf_files = sorted(self.scans_dir.glob("*.pdf")) + sorted((self.scans_dir / "audits").glob("*.pdf"))
        xlsx_files = sorted(self.scans_dir.glob("*.xlsx"))
        raw_json_files = sorted(self.scans_dir.glob("*.json"))

        evidence_files = [self._file_meta(p) for p in [*py_files, *pdf_files, *xlsx_files, *raw_json_files]]
        input_sources = [meta.path for meta in evidence_files]

        template_path = self.scans_dir / "CLARVIX_TEMPLATE_MASTER.py"
        audit_path = self.scans_dir / "clarvix_audit.py"
        filter_path = self.scans_dir / "clarvix_filter.py"

        template_text = self._read_text_safe(template_path) if template_path.exists() else ""
        audit_text = self._read_text_safe(audit_path) if audit_path.exists() else ""
        filter_text = self._read_text_safe(filter_path) if filter_path.exists() else ""
        merged_text = "\n".join([audit_text, filter_text, template_text])

        findings_hint = self._extract_findings_hint(template_text, audit_text)
        sections_present = self._extract_sections_present(merged_text)
        template_blocks = self._extract_template_blocks(template_text)

        sample_entities: list[str] = []
        for json_file in raw_json_files:
            try:
                raw_payload = json.loads(self._read_text_safe(json_file))
                if isinstance(raw_payload, dict):
                    sample_entities.extend(self._extract_sample_entities(raw_payload))
            except Exception:
                continue

        xlsx_sheets: list[str] = []
        for xlsx in xlsx_files:
            xlsx_sheets.extend(self._extract_xlsx_metadata(xlsx))
        if xlsx_sheets:
            sample_entities.extend([f"sheet:{name}" for name in xlsx_sheets[:10]])

        pdf_page_hints = [self._extract_pdf_page_hint(pdf) for pdf in pdf_files]
        if pdf_page_hints:
            sample_entities.append(f"pdf_pages_hint_max:{max(pdf_page_hints)}")

        # deterministic dedupe
        deduped_entities: list[str] = []
        for entity in sample_entities:
            if entity and entity not in deduped_entities:
                deduped_entities.append(entity)

        return ScanContext(
            input_sources=input_sources,
            template_blocks=template_blocks,
            sections_present=sections_present,
            findings_count_hint=findings_hint,
            sample_entities=deduped_entities[:30],
            evidence_files=evidence_files,
        )
