# HTML Table Rescuer

Ein robustes Python-Tool, um HTML-Tabellen für LLMs (ChatGPT, Claude, RAG) in Markdown zu retten. 
Speziell entwickelt, um Probleme mit `colspan`, `rowspan` und defektem HTML zu lösen.

## Installation

```bash
pip install table2md  # (Nachdem du es published hast)
# Oder lokal:
pip install .

Nutzung
from table2md import TableParser, ParseConfig, RowspanStrategy

html = """
<table border="1">
    <tr>
        <th>Produkt</th>
        <th>Region</th>
    </tr>
    <tr>
        <td rowspan="2">SuperWidget</td>
        <td>Nord</td>
    </tr>
    <tr>
        <td>Süd</td>
    </tr>
</table>
"""

# Config optional (Standard ist 'dito' Strategie für Rowspans)
config = ParseConfig(
    rowspan_strategy=RowspanStrategy.FILL_WITH_DITO,
    dito_prefix="siehe oben"
)

parser = TableParser(html, config)
markdown_tables = parser.parse_to_markdown()

for table in markdown_tables:
    print(table)

Output
| Produkt | Region |
| --- | --- |
| SuperWidget | Nord |
| siehe oben (SuperWidget) | Süd |
