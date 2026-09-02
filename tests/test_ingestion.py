from pathlib import Path

from pypdf import PdfWriter

from lynk.ingestion import DocumentIngestor


class FakeOcr:
    def extract_pages(self, source: Path, page_numbers: tuple[int, ...]) -> dict[int, str]:
        return {number: f"OCR text for page {number}" for number in page_numbers}


def test_ingest_text_preserves_source_and_hash(tmp_path: Path) -> None:
    source = tmp_path / "note.md"
    source.write_text("A private research note", encoding="utf-8")

    document = DocumentIngestor(tmp_path / "data").ingest(source)

    assert document.original_name == "note.md"
    assert document.stored_path.exists()
    assert document.stored_path.read_text(encoding="utf-8") == "A private research note"
    assert document.pages[0].text == "A private research note"
    assert document.extraction_status == "extracted"


def test_rejects_unsupported_document_types(tmp_path: Path) -> None:
    source = tmp_path / "program.exe"
    source.write_bytes(b"not a document")

    try:
        DocumentIngestor(tmp_path / "data").ingest(source)
    except ValueError as error:
        assert "unsupported" in str(error)
    else:
        raise AssertionError("unsupported files must be rejected")


def test_blank_pdf_is_preserved_and_flagged_for_ocr(tmp_path: Path) -> None:
    source = tmp_path / "scanned.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with source.open("wb") as stream:
        writer.write(stream)

    document = DocumentIngestor(tmp_path / "data").ingest(source)

    assert document.media_type == "application/pdf"
    assert document.extraction_status == "needs_ocr"
    assert len(document.pages) == 1
    assert document.pages[0].number == 1
    assert document.pages[0].needs_ocr is True
