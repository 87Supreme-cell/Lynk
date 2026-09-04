"""Local CLI for document-ingestion milestone."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from lynk.catalog import DocumentCatalog
from lynk.ingestion import DocumentIngestor, OCRmyPDFEngine
from lynk.model_gateway import ModelConfig, create_local_chat_model
from lynk.postgres import PostgresDocumentCatalog
from lynk.research import LocalResearchPlanner
from lynk.governed_retrieval import GovernedPostgresRetriever


def choose_document_path() -> Path:
    """Open the macOS file picker and return the user-selected file path."""
    try:
        result = subprocess.run(
            ["osascript", "-e", "POSIX path of (choose file with prompt \"Choose a document for Lynk\")"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("--choose is available on macOS only; provide a file path instead.") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError("No document was selected.") from error
    return Path(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(prog="lynk", description="Local evidence-governed research agent")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="Ingest a local text, Markdown, or PDF document")
    ingest.add_argument("path", type=Path, nargs="?", help="Path to the document to ingest")
    ingest.add_argument("--choose", action="store_true", help="Choose a document in the native macOS file picker")
    ingest.add_argument("--data-dir", type=Path, default=Path("data"))
    ingest.add_argument("--ocr", action="store_true", help="Use local ocrmypdf when text extraction is missing")
    ingest.add_argument("--storage", choices=("sqlite", "postgres"), default="sqlite")
    ingest.add_argument("--principal", default="local-owner", help="Principal granted access to this private upload")
    documents = commands.add_parser("documents", help="List ingested local documents")
    documents.add_argument("--data-dir", type=Path, default=Path("data"))
    documents.add_argument("--storage", choices=("sqlite", "postgres"), default="sqlite")
    commands.add_parser("models", help="List models exposed by the configured local runtime")
    chat = commands.add_parser("chat", help="Send a test prompt to the configured local model")
    chat.add_argument("prompt")
    research = commands.add_parser("research", help="Draft a cited answer from authorized local evidence")
    research.add_argument("question")
    research.add_argument("--principal", required=True, help="Identity with an explicit collection grant")
    args = parser.parse_args()

    if args.command == "ingest":
        if args.choose and args.path:
            parser.error("provide either a path or --choose, not both")
        if not args.choose and args.path is None:
            parser.error("path is required unless --choose is used")
        source_path = choose_document_path() if args.choose else args.path
        document = DocumentIngestor(args.data_dir, OCRmyPDFEngine() if args.ocr else None).ingest(source_path)
        if args.storage == "postgres":
            PostgresDocumentCatalog.from_environment().add(document, principal_id=args.principal)
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
    if args.command == "research":
        planner = LocalResearchPlanner(
            create_local_chat_model(ModelConfig.from_environment()), GovernedPostgresRetriever.from_environment()
        )
        draft = planner.draft(args.question, args.principal)
        print(draft.answer)
        return
    catalog = PostgresDocumentCatalog.from_environment() if args.storage == "postgres" else DocumentCatalog(args.data_dir / "lynk.sqlite3")
    for document in catalog.list_documents():
        print(f"{document['id']}  {document['extraction_status']:10}  {document['original_name']}")


if __name__ == "__main__":
    main()
