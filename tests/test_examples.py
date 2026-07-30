"""Die 13 Beispiel-Fälle aus examples/simple_usage.py als Regressionstests."""
import importlib.util
from pathlib import Path

import pytest

from table2md import TableParser

_EXAMPLES = Path(__file__).parent.parent / "examples" / "simple_usage.py"
_spec = importlib.util.spec_from_file_location("simple_usage", _EXAMPLES)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

TEST_TABLES = _module.test_tables


@pytest.mark.parametrize("name", list(TEST_TABLES))
def test_example_parses_to_valid_markdown(name):
    """Jeder Beispiel-Fall muss ohne Crash zu strukturell validem Markdown parsen."""
    tables = TableParser(TEST_TABLES[name]).parse()
    assert tables, f"'{name}' lieferte keine Tabelle"

    for t in tables:
        md = t.to_markdown()
        lines = md.strip().split("\n")
        assert len(lines) >= 2, f"'{name}': zu wenige Zeilen"
        assert set(lines[1].replace("|", "").split()) == {"---"}, f"'{name}': Trennzeile fehlt"
        # Alle Zeilen müssen gleich viele Spalten haben
        pipe_counts = {line.count("|") for line in lines}
        assert len(pipe_counts) == 1, f"'{name}': ungleiche Spaltenzahl: {md}"


def test_example_rowspan_colspan_grid():
    result = TableParser(TEST_TABLES["Mit rowspan/colspan"]).parse_to_markdown()[0]
    assert "dito (Kategorie)" in result
    assert "| Test | Alpha | Beta |" in result


def test_example_nested_tables_both_extracted():
    tables = TableParser(TEST_TABLES["Verschachtelte Tabellen"]).parse()
    # Innere und äußere Tabelle werden jeweils als eigene Tabelle extrahiert
    assert len(tables) == 2


def test_example_confluence_no_fake_headers():
    """Confluence-Tabellen ohne <th> dürfen keine Datenzeile als Header missbrauchen."""
    tables = TableParser(TEST_TABLES["Confluence Beispiel"]).parse()
    assert len(tables) == 1
    t = tables[0]
    assert t.headers == ["Column 1", "Column 2"]
    assert t.rows[0][0] == "**Allgemein**"
    assert len(t.rows) == 18
