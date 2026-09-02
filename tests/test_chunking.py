from lynk.chunking import chunk_page


def test_chunks_remain_page_aware_and_preserve_text() -> None:
    text = "alpha " * 100 + "\n\n" + "beta " * 100

    chunks = chunk_page(4, text, max_characters=300)

    assert len(chunks) > 1
    assert {chunk.page_number for chunk in chunks} == {4}
    assert "alpha" in chunks[0].text
    assert "beta" in chunks[-1].text
