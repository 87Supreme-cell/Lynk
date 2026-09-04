from lynk.chunking import chunk_page
from pathlib import Path

from lynk.domain import AccessScope, EvidenceStatus
from lynk.models import ExtractedPage, IngestedDocument
from lynk.services.chunking import PageChunker


def test_chunks_retain_document_page_version_and_lifecycle_provenance() -> None:
    document = IngestedDocument(
        "doc-1", "note.txt", Path("source"), Path("stored"), "sha256", "text/plain",
        (ExtractedPage(2, "abcdefghij"),), "extracted",
    )
    chunks = PageChunker(max_characters=6, overlap_characters=2).chunk(
        document, 3, EvidenceStatus.PRIVATE, AccessScope.PRIVATE
    )
    assert [(chunk.content, chunk.start_offset, chunk.end_offset) for chunk in chunks] == [
        ("abcdef", 0, 6), ("efghij", 4, 10)
    ]
    assert all(chunk.page_number == 2 and chunk.document_version == 3 for chunk in chunks)
    assert all(chunk.content_hash == "sha256" and chunk.status is EvidenceStatus.PRIVATE for chunk in chunks)


def test_chunks_remain_page_aware_and_preserve_text() -> None:
    text = "alpha " * 100 + "\n\n" + "beta " * 100

    chunks = chunk_page(4, text, max_characters=300)

    assert len(chunks) > 1
    assert {chunk.page_number for chunk in chunks} == {4}
    assert "alpha" in chunks[0].text
    assert "beta" in chunks[-1].text
