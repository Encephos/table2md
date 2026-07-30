import json
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import requests
import typer

from .core import TableParser
from .models import ParseConfig, RowspanStrategy

app = typer.Typer(add_completion=False)


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"


def load_source(source: Optional[str]) -> str:
    """Lädt HTML von stdin ('-' oder Pipe), einer URL oder einer Datei."""
    if source is None or source == "-":
        if source is None and sys.stdin.isatty():
            typer.echo("No source given. Pass a file path, URL, or '-' for stdin.", err=True)
            raise typer.Exit(code=1)
        return sys.stdin.read()

    if source.startswith(("http://", "https://")):
        try:
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            typer.echo(f"Error fetching URL: {e}", err=True)
            raise typer.Exit(code=1)

    path = Path(source)
    if not path.exists():
        typer.echo(f"File not found: {path}", err=True)
        raise typer.Exit(code=1)
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        typer.echo(f"Error reading file: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def extract(
    source: Optional[str] = typer.Argument(
        None, help="URL, file path, or '-' for stdin. Reads stdin when piped without argument."
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.MARKDOWN, "--format", "-f", help="Output format."
    ),
    strategy: RowspanStrategy = typer.Option(
        RowspanStrategy.FILL_WITH_DITO, "--strategy", "-s", help="How to fill rowspan cells."
    ),
    dito_prefix: str = typer.Option("dito", help="Prefix used by the fill_dito strategy."),
    keep_links: bool = typer.Option(True, "--links/--no-links", help="Keep <a> tags as Markdown links."),
    keep_bold: bool = typer.Option(True, "--bold/--no-bold", help="Keep bold formatting."),
    keep_italic: bool = typer.Option(True, "--italic/--no-italic", help="Keep italic formatting."),
    parser: str = typer.Option("lxml", help="BeautifulSoup parser backend (lxml, html.parser)."),
    table: Optional[int] = typer.Option(
        None, "--table", "-t", help="Extract only the table with this index (0-based)."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write to this file instead of stdout."
    ),
):
    """Extract HTML tables and convert them to Markdown, JSON, or CSV."""
    html_content = load_source(source)

    config = ParseConfig(
        rowspan_strategy=strategy,
        dito_prefix=dito_prefix,
        keep_links=keep_links,
        keep_bold=keep_bold,
        keep_italic=keep_italic,
        parser_library=parser,
    )
    tables = TableParser(html_content, config).parse()

    if not tables:
        typer.echo("No tables found.", err=True)
        raise typer.Exit(code=1)

    if table is not None:
        if not 0 <= table < len(tables):
            typer.echo(f"Table index {table} out of range ({len(tables)} tables found).", err=True)
            raise typer.Exit(code=1)
        tables = [tables[table]]

    if format == OutputFormat.MARKDOWN:
        text = "\n\n".join(t.to_markdown() for t in tables)
    elif format == OutputFormat.JSON:
        if len(tables) == 1:
            text = tables[0].to_json()
        else:
            text = json.dumps(
                [json.loads(t.to_json()) for t in tables], indent=2, ensure_ascii=False
            )
    else:  # CSV
        if len(tables) > 1 and output is not None:
            # Eine Datei pro Tabelle: name_1.csv, name_2.csv, ...
            suffix = output.suffix or ".csv"
            for i, t in enumerate(tables, start=1):
                target = output.with_name(f"{output.stem}_{i}{suffix}")
                target.write_text(t.to_csv(), encoding="utf-8")
                typer.echo(f"Wrote {target}", err=True)
            return
        if len(tables) > 1:
            typer.echo(
                f"Warning: {len(tables)} tables found; CSV output is concatenated. "
                "Use --table to pick one or --output to write separate files.",
                err=True,
            )
        text = "\n".join(t.to_csv() for t in tables)

    if output is not None:
        output.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        typer.echo(f"Wrote {output}", err=True)
    else:
        typer.echo(text)


if __name__ == "__main__":
    app()
