from bs4 import BeautifulSoup, Tag
from typing import List
from .models import ParseConfig, ParsedTable, RowspanStrategy
from .cleaner import clean_cell_content

class TableParser:
    def __init__(self, html_content: str, config: ParseConfig = None):
        if config is None:
            self.config = ParseConfig()
        else:
            self.config = config
            
        self.soup = BeautifulSoup(html_content, self.config.parser_library)

    def parse(self) -> List[ParsedTable]:
        """Gibt eine Liste von ParsedTable Objekten zurück."""
        tables = self.soup.find_all('table')
        results = []
        for table in tables:
            parsed_table = self._process_single_table(table)
            if parsed_table:
                results.append(parsed_table)
        return results

    def parse_to_markdown(self) -> List[str]:
        """Convenience: Gibt direkt Markdown-Strings zurück."""
        return [t.to_markdown() for t in self.parse()]

    def _process_single_table(self, table: Tag) -> ParsedTable:
        # FIX 1: Nur Zeilen (<tr>) nehmen, die direkt zu DIESER Tabelle gehören.
        all_trs = table.find_all('tr')
        rows = [tr for tr in all_trs if tr.find_parent('table') is table]
        
        if not rows:
            return None

        grid = {} # (row, col) -> content
        max_col = 0
        occupied_cells = set() # (row, col)

        # Pre-Scan um Grid aufzubauen
        for r_idx, row in enumerate(rows):
            # FIX 2: Nur Zellen (td/th) nehmen, die direkt zu DIESER Zeile gehören.
            all_cells = row.find_all(['td', 'th'])
            cells = [cell for cell in all_cells if cell.find_parent('tr') is row]
            
            c_idx = 0 

            for cell in cells:
                # Überspringe belegte Zellen
                while (r_idx, c_idx) in occupied_cells:
                    c_idx += 1

                colspan = int(cell.get('colspan', 1))
                rowspan = int(cell.get('rowspan', 1))
                
                # Inhalt säubern
                content = clean_cell_content(cell, self.config)
                
                # Strategie anwenden
                for r_offset in range(rowspan):
                    for c_offset in range(colspan):
                        target_r = r_idx + r_offset
                        target_c = c_idx + c_offset
                        occupied_cells.add((target_r, target_c))

                        # Logik für Zell-Inhalt
                        if r_offset == 0 and c_offset == 0:
                            # Das ist die Original-Zelle (oben links)
                            grid[(target_r, target_c)] = content
                        
                        elif r_offset > 0:
                            # Das ist eine vertikale Erweiterung (rowspan)
                            if self.config.rowspan_strategy == RowspanStrategy.FILL_WITH_DITO:
                                grid[(target_r, target_c)] = f"{self.config.dito_prefix} ({content})"
                            elif self.config.rowspan_strategy == RowspanStrategy.REPEAT_VALUE:
                                grid[(target_r, target_c)] = content
                            else:
                                grid[(target_r, target_c)] = "" # Empty
                        
                        else:
                            # Das ist eine horizontale Erweiterung (colspan)
                            # Markdown mag hier leere Zellen
                            grid[(target_r, target_c)] = ""

                c_idx += colspan
            
            max_col = max(max_col, c_idx)

        if max_col == 0:
            return None

        # --- Intelligente Header-Erkennung ---
        first_row_has_th = False
        if rows:
            # Prüfen, ob die erste Zeile <th> Tags hat oder in einem <thead> liegt
            has_th = rows[0].find('th') is not None
            in_thead = rows[0].find_parent('thead') is not None
            
            if has_th or in_thead:
                first_row_has_th = True

        if first_row_has_th:
            # Zeile 0 ist ein echter Header
            headers = [grid.get((0, c), "") for c in range(max_col)]
            start_row = 1
        else:
            # Kein Header gefunden -> Dummy-Header generieren, Zeile 0 als Daten behandeln
            headers = [f"Column {c+1}" for c in range(max_col)]
            start_row = 0
            
        body_rows = []
        for r in range(start_row, len(rows)):
            row_data = [grid.get((r, c), "") for c in range(max_col)]
            body_rows.append(row_data)

        return ParsedTable(headers=headers, rows=body_rows)
