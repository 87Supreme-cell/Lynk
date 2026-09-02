"""Local CLI for document-ingestion milestone."""

from __future__ import annotations

import argparse
from pathlib import Path

from lynk.catalog import DocumentCatalog
from lynk.ingestion import DocumentIngestor, OCRmyPDFEngine
from lynk.model_gateway import ModelConfig, create_local_chat_model
from lynk.postgres import PostgresDocumentCatalog


def main() -> None:
    parser = argparse.ArgumentParser(prog="lynk", description="Local evidence-governed research agent")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="Ingest a local text, Markdown, or PDF document")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--data-dir", type=Path, default=Path("data"))
    ingest.add_argument("--ocr", action="store_true", help="Use local ocrmypdf when text extraction is missing")
    ingest.add_argument("--storage", choices=("sqlite", "postgres"), default="sqlite")
    documents = commands.add_parser("documents", help="List ingested local documents")
    documents.add_argument("--data-dir", type=Path, default=Path("data"))
    documents.add_argument("--storage", choices=("sqlite", "postgres"), default="sqlite")
    commands.add_parser("models", help="List models exposed by the configured local runtime")
    chat = commands.add_parser("chat", help="Send a test prompt to the configured local model")
    chat.add_argument("prompt")
    args = parser.parse_args()

    if args.command == "ingest":
        document = DocumentIngestor(args.data_dir, OCRmyPDFEngine() if args.ocr else None).ingest(args.path)
        if args.storage == "postgres":
            PostgresDocumentCatalog.from_environment().add(document)
        else:
            DocumentCatalog(args.data_dir / "lynk.sqlite3").add(document)
        print(f"Ingested {document.original_name}: {document.document_id} ({document.extraction_status})")
        return
    if args.command == "models":
        for model in create_local_chat_model(ModelConfig.from_environment()).list_models():
            print(model)
        return
    if args.command == "chat":
        print(create_local_chat_model(ModelConfig.from_environment()).complete(args.prompt))
        return
    catalog = PostgresDocumentCatalog.from_environment() if args.storage == "postgres" else DocumentCatalog(args.data_dir / "lynk.sqlite3")
    for document in catalog.list_documents():
        print(f"{document['id']}  {document['extraction_status']:10}  {document['original_name']}")


if __name__ == "__main__":
    main()
