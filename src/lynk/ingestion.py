"""Safe, local document ingestion with page-level provenance."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Protocol
from uuid import uuid4

from lynk.models import ExtractedPage, IngestedDocument


class OcrEngine(Protocol):
    """An optional local OCR adapter used only for pages requiring OCR."""

    def extract_pages(self, source: Path, page_numbers: tuple[int, ...]) -> dict[int, str]: ...


class OCRmyPDFEngine:
    """Local OCR adapter backed by the optional `ocrmypdf` executable."""

    def extract_pages(self, source: Path, page_numbers: tuple[int, ...]) -> dict[int, str]:
        if not shutil.which("ocrmypdf"):
            raise RuntimeError("OCR is required but ocrmypdf is not installed")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ocr.pdf"
            subprocess.run(
                ["ocrmypdf", "--skip-text", "--quiet", str(source), str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            return {page.number: page.text for page in PypdfExtractor().extract(output) if page.number in page_numbers}


class PypdfExtractor:
    """Extract PDF text while retaining page boundaries."""

    def extract(self, source: Path) -> tuple[ExtractedPage, ...]:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - dependency contract
            raise RuntimeError("PDF ingestion requires pypdf; install the project dependencies") from exc
        reader = PdfReader(str(source))
        return tuple(
            ExtractedPage(number=index, text=(page.extract_text() or "").strip(), needs_ocr=not bool((page.extract_text() or "").strip()))
            for index, page in enumerate(reader.pages, start=1)
        )


class DocumentIngestor:
    """Copies approved local documents and extracts page-level text locally."""

    _TEXT_SUFFIXES: ClassVar[frozenset[str]] = frozenset({".txt", ".md", ".rst"})

    def __init__(self, data_directory: Path, ocr: OcrEngine | None = None) -> None:
        self.data_directory = data_directory
        self.raw_directory = data_directory / "raw"
        self.ocr = ocr

    def ingest(self, source: Path) -> IngestedDocument:
        source = source.expanduser().resolve(strict=True)
        if not source.is_file():
            raise ValueError(f"document is not a regular file: {source}")
        suffix = source.suffix.lower()
        if suffix not in self._TEXT_SUFFIXES | {".pdf"}:
            raise ValueError(f"unsupported document type: {suffix or '<none>'}")
        document_id = str(uuid4())
        content_hash = self._hash(source)
        self.raw_directory.mkdir(parents=True, exist_ok=True)
        stored_path = self.raw_directory / f"{document_id}{suffix}"
        shutil.copy2(source, stored_path)
        pages, media_type = self._extract(stored_path, suffix)
        missing = tuple(page.number for page in pages if page.needs_ocr)
        if missing and self.ocr:
            ocr_text = self.ocr.extract_pages(stored_path, missing)
            pages = tuple(
                ExtractedPage(page.number, ocr_text.get(page.number, page.text), page.number not in ocr_text)
                if page.number in missing
                else page
                for page in pages
            )
        status = "needs_ocr" if any(page.needs_ocr for page in pages) else "extracted"
        return IngestedDocument(
            document_id=document_id,
            original_name=source.name,
            source_path=source,
            stored_path=stored_path,
            content_hash=content_hash,
            media_type=media_type,
            pages=pages,
            extraction_status=status,
        )

    def _extract(self, source: Path, suffix: str) -> tuple[tuple[ExtractedPage, ...], str]:
        if suffix == ".pdf":
            return PypdfExtractor().extract(source), "application/pdf"
        return (ExtractedPage(number=1, text=source.read_text(encoding="utf-8")),), "text/plain"

    @staticmethod
    def _hash(source: Path) -> str:
        digest = hashlib.sha256()
        with source.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp for persisted provenance."""
    return datetime.now(UTC).isoformat()
