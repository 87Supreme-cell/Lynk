"""Page-aware chunking that cannot discard evidence provenance."""

from __future__ import annotations

from lynk.domain import AccessScope, Chunk, EvidenceStatus
from lynk.models import IngestedDocument


class PageChunker:
    """Split extracted page text into bounded, traceable character spans."""

    def __init__(self, max_characters: int = 1_200, overlap_characters: int = 150) -> None:
        if max_characters < 1:
            raise ValueError("max_characters must be positive")
        if not 0 <= overlap_characters < max_characters:
            raise ValueError("overlap_characters must be non-negative and smaller than max_characters")
        self.max_characters = max_characters
        self.overlap_characters = overlap_characters

    def chunk(
        self,
        document: IngestedDocument,
        document_version: int,
        status: EvidenceStatus,
        access_scope: AccessScope,
    ) -> tuple[Chunk, ...]:
        chunks: list[Chunk] = []
        for page in document.pages:
            text = page.text.strip()
            if page.needs_ocr or not text:
                continue
            start = 0
            while start < len(text):
                end = min(start + self.max_characters, len(text))
                chunks.append(
                    Chunk(
                        chunk_index=len(chunks),
                        page_number=page.number,
                        start_offset=start,
                        end_offset=end,
                        content=text[start:end],
                        document_id=document.document_id,
                        document_version=document_version,
                        content_hash=document.content_hash,
                        status=status,
                        access_scope=access_scope,
                    )
                )
                if end == len(text):
                    break
                start = end - self.overlap_characters
        return tuple(chunks)
