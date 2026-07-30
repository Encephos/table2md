"""Tests für die Typer-CLI (table2md)."""
import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from table2md.cli import app

runner = CliRunner()

SIMPLE_HTML = """
<table>
    <tr><th>Name</th><th>Alter</th></tr>
    <tr><td>Max</td><td>25</td></tr>
</table>
"""

TWO_TABLES_HTML = SIMPLE_HTML + """
<table>
    <tr><th>Stadt</th></tr>
    <tr><td>Berlin</td></tr>
</table>
"""


def _write_html(tmp_path, content=SIMPLE_HTML):
    f = tmp_path / "input.html"
    f.write_text(content, encoding="utf-8")
    return f


def test_file_to_markdown(tmp_path):
    f = _write_html(tmp_path)
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 0
    assert "| Name | Alter |" in result.output
    assert "| Max | 25 |" in result.output


def test_file_to_json(tmp_path):
    f = _write_html(tmp_path)
    result = runner.invoke(app, [str(f), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == [{"Name": "Max", "Alter": "25"}]


def test_file_to_csv(tmp_path):
    f = _write_html(tmp_path)
    result = runner.invoke(app, [str(f), "--format", "csv"])
    assert result.exit_code == 0
    assert "Name,Alter" in result.output
    assert "Max,25" in result.output


def test_stdin_dash():
    result = runner.invoke(app, ["-"], input=SIMPLE_HTML)
    assert result.exit_code == 0
    assert "| Max | 25 |" in result.output


def test_stdin_pipe_without_argument():
    """`curl … | table2md` — gepipte Eingabe ohne Quell-Argument."""
    result = runner.invoke(app, [], input=SIMPLE_HTML)
    assert result.exit_code == 0
    assert "| Max | 25 |" in result.output


def test_url_uses_timeout():
    mock_response = MagicMock()
    mock_response.text = SIMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    with patch("table2md.cli.requests.get", return_value=mock_response) as mock_get:
        result = runner.invoke(app, ["https://example.com/page.html"])
    assert result.exit_code == 0
    assert "| Max | 25 |" in result.output
    assert mock_get.call_args.kwargs.get("timeout") == 30


def test_invalid_strategy_fails():
    """Tippfehler in --strategy müssen ein Fehler sein, kein stiller Fallback."""
    result = runner.invoke(app, ["-", "--strategy", "quatsch"], input=SIMPLE_HTML)
    assert result.exit_code != 0


def test_strategy_repeat(tmp_path):
    html = """
    <table>
        <tr><td rowspan="2">Test</td><td>A</td></tr>
        <tr><td>B</td></tr>
    </table>
    """
    f = _write_html(tmp_path, html)
    result = runner.invoke(app, [str(f), "--strategy", "repeat"])
    assert result.exit_code == 0
    assert result.output.count("Test") == 2


def test_no_bold(tmp_path):
    f = _write_html(tmp_path, "<table><tr><td><b>Fett</b></td></tr></table>")
    result = runner.invoke(app, [str(f), "--no-bold"])
    assert result.exit_code == 0
    assert "**" not in result.output
    assert "Fett" in result.output


def test_table_index(tmp_path):
    f = _write_html(tmp_path, TWO_TABLES_HTML)
    result = runner.invoke(app, [str(f), "--table", "1"])
    assert result.exit_code == 0
    assert "Berlin" in result.output
    assert "Max" not in result.output


def test_table_index_out_of_range(tmp_path):
    f = _write_html(tmp_path, TWO_TABLES_HTML)
    result = runner.invoke(app, [str(f), "--table", "99"])
    assert result.exit_code != 0


def test_output_file(tmp_path):
    f = _write_html(tmp_path)
    out = tmp_path / "out.md"
    result = runner.invoke(app, [str(f), "--output", str(out)])
    assert result.exit_code == 0
    assert "| Max | 25 |" in out.read_text(encoding="utf-8")


def test_multi_table_csv_output_files(tmp_path):
    """Mehrere Tabellen + CSV + --output → eine Datei pro Tabelle."""
    f = _write_html(tmp_path, TWO_TABLES_HTML)
    out = tmp_path / "data.csv"
    result = runner.invoke(app, [str(f), "--format", "csv", "--output", str(out)])
    assert result.exit_code == 0
    assert (tmp_path / "data_1.csv").exists()
    assert (tmp_path / "data_2.csv").exists()
    assert "Berlin" in (tmp_path / "data_2.csv").read_text(encoding="utf-8")


def test_file_not_found():
    result = runner.invoke(app, ["/nonexistent/file.html"])
    assert result.exit_code == 1


def test_no_tables_found():
    result = runner.invoke(app, ["-"], input="<html><body>nix</body></html>")
    assert result.exit_code == 1
