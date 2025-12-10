from dataclasses import dataclass
from enum import Enum

class RowspanStrategy(Enum):
    """Strategie für vertikal verbundene Zellen (rowspan)."""
    FILL_WITH_DITO = "fill_dito"   # Schreibt 'dito (Wert)' in die unteren Zellen
    REPEAT_VALUE = "repeat"        # Wiederholt den Wert 1:1
    EMPTY = "empty"                # Lässt die unteren Zellen leer

@dataclass
class ParseConfig:
    """Konfiguration für den Parsing-Prozess."""
    rowspan_strategy: RowspanStrategy = RowspanStrategy.FILL_WITH_DITO
    dito_prefix: str = "dito"  # Nur relevant für FILL_WITH_DITO
    
    # Formatierungs-Optionen
    keep_links: bool = True    # <a href="..."> behalten
    keep_bold: bool = True     # <b> / <strong> behalten
    keep_italic: bool = True   # <i> / <em> behalten
    
    # Technisches
    parser_library: str = "lxml" # oder 'html.parser'

@dataclass
class MarkdownTable:
    """Das Ergebnis einer Konvertierung."""
    headers: list[str]
    rows: list[list[str]]
    
    def to_string(self) -> str:
        """Rendert die Tabelle zu einem Markdown-String."""
        if not self.headers and not self.rows:
            return ""
            
        lines = []
        
        # Grid Dimension bestimmen
        cols = len(self.headers)
        if cols == 0 and self.rows:
            cols = len(self.rows[0])
            # Leere Header generieren, falls keine <th> da waren
            header_line = f"| {' | '.join([''] * cols)} |"
        else:
            header_line = f"| {' | '.join(self.headers)} |"
            
        lines.append(header_line)
        lines.append(f"| {' | '.join(['---'] * cols)} |")
        
        for row in self.rows:
            # Padding: Zeile auffüllen falls zu kurz
            current_row = row + [""] * (cols - len(row))
            # Abschneiden falls zu lang
            current_row = current_row[:cols]
            lines.append(f"| {' | '.join(current_row)} |")
            
        return "\n".join(lines)
        