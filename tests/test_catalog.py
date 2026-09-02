from pathlib import Path

from lynk.catalog import DocumentCatalog
from lynk.ingestion import DocumentIngestor


def test_catalog_persists_document_and_pages(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("evidence", encoding="utf-8")
    data_directory = tmp_path / "data"
    document = DocumentIngestor(data_directory).ingest(source)

    catalog = DocumentCatalog(data_directory / "lynk.sqlite3")
    catalog.add(document)

    documents = catalog.list_documents()
    assert len(documents) == 1
    assert documents[0]["id"] == document.document_id
    assert documents[0]["original_name"] == "source.txt"
