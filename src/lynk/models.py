"""Typed records for local document provenance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractedPage:
    """Text and OCR state for one one-based page."""

    number: int
    text: str
    needs_ocr: bool = False


@dataclass(frozen=True)
class IngestedDocument:
    """A document stored locally with its extracted page evidence."""

    document_id: str
    original_name: str
    source_path: Path
    stored_path: Path
    content_hash: str
    media_type: str
    pages: tuple[ExtractedPage, ...]
    extraction_status: str

