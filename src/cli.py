"""CLI interface for RAG One."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path

from src.rag_engine import RAGEngine
from src.config import DOCUMENTS_PATH, OLLAMA_BASE_URL, OLLAMA_MODEL

console = Console()


@click.group()
def cli():
    """RAG One - A RAG system using LangChain and Ollama."""
    pass


@cli.command()
@click.option(
    "--documents-path",
    "-d",
    default=DOCUMENTS_PATH,
    help="Path to documents directory",
    type=click.Path(exists=True),
)
@click.option(
    "--ollama-url",
    default=OLLAMA_BASE_URL,
    help="Ollama server URL",
)
@click.option(
    "--ollama-model",
    default=OLLAMA_MODEL,
    help="Ollama model name",
)
def index(documents_path, ollama_url, ollama_model):
    """Index documents and create vector store."""
    console.print(Panel.fit("🔍 Indexing Documents", style="bold blue"))
    console.print(f"Documents path: {documents_path}")
    console.print(f"Ollama URL: {ollama_url}")
    console.print(f"Ollama model: {ollama_model}\n")

    try:
        engine = RAGEngine(
            ollama_url=ollama_url,
            ollama_model=ollama_model,
        )
        engine.setup_from_documents(documents_path)
        console.print("✅ [bold green]Indexing complete![/bold green]")
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    "--question",
    "-q",
    help="Question to ask",
)
@click.option(
    "--ollama-url",
    default=OLLAMA_BASE_URL,
    help="Ollama server URL",
)
@click.option(
    "--ollama-model",
    default=OLLAMA_MODEL,
    help="Ollama model name",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive mode",
)
def query(question, ollama_url, ollama_model, interactive):
    """Query the RAG system."""
    console.print(Panel.fit("💬 RAG Query System", style="bold blue"))

    try:
        engine = RAGEngine(
            ollama_url=ollama_url,
            ollama_model=ollama_model,
        )
        engine.setup_from_existing_store()
    except Exception as e:
        console.print(f"❌ [bold red]Error initializing engine:[/bold red] {str(e)}")
        console.print("\n💡 [yellow]Tip:[/yellow] Run 'rag-one index' first to create the vector store.")
        sys.exit(1)

    if interactive:
        console.print("\n[bold green]Interactive mode activated![/bold green]")
        console.print("Type your questions (or 'quit' to exit)\n")

        while True:
            try:
                user_input = console.input("[bold cyan]You:[/bold cyan] ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if not user_input.strip():
                    continue

                with console.status("[bold green]Thinking..."):
                    result = engine.query(user_input)

                console.print("\n[bold magenta]Assistant:[/bold magenta]")
                console.print(Panel(result["answer"], style="green"))

                # Show sources
                if result["source_documents"]:
                    console.print("\n[dim]📚 Sources:[/dim]")
                    for i, doc in enumerate(result["source_documents"][:3], 1):
                        source = doc.metadata.get("source", "Unknown")
                        console.print(f"  {i}. {Path(source).name}")
                console.print()

            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"\n❌ [bold red]Error:[/bold red] {str(e)}\n")

    else:
        if not question:
            console.print("❌ [bold red]Error:[/bold red] Please provide a question with -q or use -i for interactive mode")
            sys.exit(1)

        try:
            console.print(f"\n[bold cyan]Question:[/bold cyan] {question}\n")
            with console.status("[bold green]Thinking..."):
                result = engine.query(question)

            console.print("[bold magenta]Answer:[/bold magenta]")
            console.print(Panel(result["answer"], style="green"))

            # Show sources
            if result["source_documents"]:
                console.print("\n[dim]📚 Sources:[/dim]")
                for i, doc in enumerate(result["source_documents"][:3], 1):
                    source = doc.metadata.get("source", "Unknown")
                    console.print(f"  {i}. {Path(source).name}")

        except Exception as e:
            console.print(f"❌ [bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)


@cli.command()
def info():
    """Show system information."""
    console.print(Panel.fit("ℹ️  RAG One System Information", style="bold blue"))
    console.print(f"Documents path: {DOCUMENTS_PATH}")
    console.print(f"Ollama URL: {OLLAMA_BASE_URL}")
    console.print(f"Ollama model: {OLLAMA_MODEL}")

    # Check if vector store exists
    from src.config import VECTOR_STORE_DIR
    if VECTOR_STORE_DIR.exists() and any(VECTOR_STORE_DIR.iterdir()):
        console.print("✅ Vector store: [green]exists[/green]")
    else:
        console.print("❌ Vector store: [red]not found[/red]")
        console.print("   Run 'rag-one index' to create it")


if __name__ == "__main__":
    cli()
