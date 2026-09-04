"""Validate model citation identifiers against the supplied evidence packet."""

from __future__ import annotations

import re
from collections.abc import Sequence

_CITATION = re.compile(r"\[S(\d+)\]")


class CitationValidationError(ValueError):
    pass


def validate_citations(answer: str, evidence: Sequence[object]) -> None:
    """Reject uncited answers and citations outside the current evidence packet."""
    cited = {int(value) for value in _CITATION.findall(answer)}
    if not cited:
        raise CitationValidationError("draft contains no evidence citations")
    invalid = cited - set(range(1, len(evidence) + 1))
    if invalid:
        raise CitationValidationError(f"draft cites evidence not provided: {sorted(invalid)}")
