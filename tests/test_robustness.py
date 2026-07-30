"""Tests für Robustheit bei kaputtem Real-World-HTML (Spans, Kommentare, Grid-Grenzen)."""
import pytest
from table2md import TableParser, ParseConfig, ParsedTable, RowspanStrategy


def test_public_api_imports():
    """Die Kernklassen müssen direkt aus dem Paket importierbar sein."""
    assert TableParser is not None
    assert ParseConfig is not None
    assert ParsedTable is not None
    assert RowspanStrategy is not None


@pytest.mark.parametrize("bad_span", ['""', '"abc"', '"0"', '"-3"'])
def test_invalid_colspan_does_not_crash_or_drop_content(bad_span):
    """Ungültige colspan-Werte dürfen weder crashen noch Zellinhalt verschlucken."""
    html = f"""
    <table>
        <tr><td colspan={bad_span}>Wichtig</td><td>Daneben</td></tr>
    </table>
    """
    parser = TableParser(html)
    result = parser.parse_to_markdown()[0]

    assert "Wichtig" in result
    assert "Daneben" in result


def test_invalid_rowspan_does_not_crash():
    """Ungültige rowspan-Werte zählen als 1."""
    html = """
    <table>
        <tr><td rowspan="abc">A</td><td>B</td></tr>
        <tr><td>C</td><td>D</td></tr>
    </table>
    """
    parser = TableParser(html)
    result = parser.parse_to_markdown()[0]
    assert "A" in result and "D" in result


def test_huge_rowspan_is_capped_at_table_end():
    """rowspan="10000" darf kein Riesen-Grid allozieren; Tabelle endet an der letzten Zeile."""
    html = """
    <table>
        <tr><td rowspan="10000">Oben</td><td>R1</td></tr>
        <tr><td>R2</td></tr>
    </table>
    """
    parser = TableParser(html)
    result = parser.parse_to_markdown()[0]

    # Wie im Browser: keine Phantom-Zeilen hinter der letzten <tr>
    lines = result.strip().split("\n")
    assert len(lines) == 4  # Header + Trenner + 2 Datenzeilen (kein <th> -> Dummy-Header)
    assert "dito (Oben)" in lines[-1]


def test_rowspan_overflowing_last_row():
    """rowspan über das Tabellenende hinaus wird sauber gekappt statt zu crashen."""
    html = """
    <table>
        <tr><th>H1</th><th>H2</th></tr>
        <tr><td rowspan="5">A</td><td>B</td></tr>
    </table>
    """
    parser = TableParser(html)
    tables = parser.parse()
    assert len(tables) == 1
    assert tables[0].rows == [["A", "B"]]


def test_html_comments_are_ignored():
    """HTML-Kommentare dürfen nicht als Zelltext im Output landen."""
    html = """
    <table>
        <tr><td>Wert<!-- interne Notiz --></td></tr>
    </table>
    """
    parser = TableParser(html)
    result = parser.parse_to_markdown()[0]

    assert "Wert" in result
    assert "interne Notiz" not in result


def test_comment_only_cell_is_empty():
    html = """
    <table>
        <tr><td><!-- nur kommentar --></td><td>Inhalt</td></tr>
    </table>
    """
    parser = TableParser(html)
    result = parser.parse_to_markdown()[0]
    assert "nur kommentar" not in result
    assert "Inhalt" in result
