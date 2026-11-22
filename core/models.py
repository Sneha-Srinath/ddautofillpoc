"""Pydantic models shared by the engine and the UI."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

FieldType = Literal["text", "checkbox", "radio", "dropdown"]
Status = Literal["Filled", "Review", "Missing", "Unmapped", "Manual"]
MatchMethod = Literal["exact", "synonym", "fuzzy", "semantic", "rule", "admin"]


class ExtractedJson(BaseModel):
    """Extraction contract: client_id is mandatory; any nested structure is allowed."""
    model_config = {"extra": "allow"}
    client_id: str = Field(min_length=1)
    client_name: str
    extracted_at: str
    source_documents: list[str] = []

    @model_validator(mode="after")
    def _has_payload(self):
        if not (self.model_extra or {}):
            raise ValueError("extracted JSON has no data sections")
        return self


class DiscoveredField(BaseModel):
    name: str
    label: str = ""
    type: FieldType
    options: list[str] = []
    page: int = 1
    rect: tuple[float, float, float, float] = (0, 0, 0, 0)
    max_length: int | None = None


class SourceMatch(BaseModel):
    path: str
    method: MatchMethod
    score: float


class FieldMapping(BaseModel):
    type: FieldType
    label: str = ""
    format: str = "text"
    options: list[str] = []
    max_length: int | None = None
    manual: bool = False
    sources: list[str] = []                 # ordered by precedence
    match: dict[str, SourceMatch] = {}      # keyed by "json" / "db"
    concept: str | None = None
    reviewed_by: str | None = None
    reviewed_on: str | None = None


class TemplateConfig(BaseModel):
    """Registry record for one uploaded template. client_id is the company's unique identifier
    and the key into its extracted JSON and database rows."""
    template_id: str
    client_id: str
    company_name: str = ""
    name: str
    format: Literal["pdf", "docx", "html"] = "pdf"
    issuer: str = ""
    file: str
    field_count: int = 0
    uploaded_on: str = ""
    uploaded_by: str = ""
    version: int = 1
    mapping_version: int = 0          # 0 = matched automatically at fill time
    fields: dict[str, FieldMapping] = {}


class SourceEntry(BaseModel):
    path: str
    kind: Literal["json", "db"]
    value: Any = None
    confidence: float | None = None
    source_ref: str | None = None
    variants: list[str] = []                # normalized phrases describing this path


class ResolvedField(BaseModel):
    name: str
    label: str
    type: FieldType
    value: Any = None                       # str for text/radio/dropdown, bool|None for checkbox
    display: str = ""
    source: Literal["JSON", "DB", "User", "-"] = "-"
    source_path: str = ""
    confidence: float | None = None
    status: Status
    note: str = ""
    options: list[str] = []


class FillResult(BaseModel):
    template_id: str
    client_id: str
    client_name: str
    fields: list[ResolvedField]
    output_path: str
    output_name: str
    elapsed_ms: int
    input_hash: str

    def counts(self) -> dict[str, int]:
        out = {s: 0 for s in ("Filled", "Review", "Missing", "Unmapped", "Manual")}
        for f in self.fields:
            out[f.status] += 1
        return out
