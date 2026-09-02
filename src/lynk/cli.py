"""Local CLI for document-ingestion milestone."""

from __future__ import annotations

import argparse
from pathlib import Path

from lynk.catalog import DocumentCatalog
from lynk.ingestion import DocumentIngestor, OCRmyPDFEngine


def main() -> None:
    parser = argparse.ArgumentParser(prog="lynk", description="Local evidence-governed research agent")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="Ingest a local text, Markdown, or PDF document")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--data-dir", type=Path, default=Path("data"))
    ingest.add_argument("--ocr", action="store_true", help="Use local ocrmypdf when text extraction is missing")
    documents = commands.add_parser("documents", help="List ingested local documents")
    documents.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    if args.command == "ingest":
        document = DocumentIngestor(args.data_dir, OCRmyPDFEngine() if args.ocr else None).ingest(args.path)
        DocumentCatalog(args.data_dir / "lynk.sqlite3").add(document)
        print(f"Ingested {document.original_name}: {document.document_id} ({document.extraction_status})")
        return
    for document in DocumentCatalog(args.data_dir / "lynk.sqlite3").list_documents():
        print(f"{document['id']}  {document['extraction_status']:10}  {document['original_name']}")


if __name__ == "__main__":
    main()

