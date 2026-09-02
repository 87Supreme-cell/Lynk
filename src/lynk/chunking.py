"""Deterministic, page-aware chunks for retrieval and page citations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageChunk:
    """A chunk that retains the page from which it was extracted."""

    page_number: int
    index: int
    text: str


def chunk_page(page_number: int, text: str, max_characters: int = 1600) -> list[PageChunk]:
    """Split one page at paragraph boundaries without crossing page citations."""
    if max_characters <= 0:
        raise ValueError("max_characters must be positive")
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[PageChunk] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if current and len(candidate) > max_characters:
            chunks.append(PageChunk(page_number, len(chunks), current))
            current = paragraph
        else:
            current = candidate
        while len(current) > max_characters:
            chunks.append(PageChunk(page_number, len(chunks), current[:max_characters]))
            current = current[max_characters:].lstrip()
    if current:
        chunks.append(PageChunk(page_number, len(chunks), current))
    return chunks
