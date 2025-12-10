from bs4 import BeautifulSoup, Tag
from typing import List
from .models import ParseConfig, MarkdownTable, RowspanStrategy
from .cleaner import clean_cell_content

class TableParser:
    def __init__(self, html_content: str, config: ParseConfig = None):
        if config is None:
            self.config = ParseConfig()
        else:
            self.config = config
            
        self.soup = BeautifulSoup(html_content, self.config.parser_library)

    def parse(self) -> List[MarkdownTable]:
        """Gibt eine Liste von MarkdownTable Objekten zurück."""
        tables = self.soup.find_all('table')
        results = []
        for table in tables:
            md_table = self._process_single_table(table)
            if md_table:
                results.append(md_table)
        return results

    def parse_to_markdown(self) -> List[str]:
        """Convenience: Gibt direkt Strings zurück."""
        return [t.to_string() for t in self.parse()]

    def _process_single_table(self, table: Tag) -> MarkdownTable:
        rows = table.find_all('tr')
        if not rows:
            return None

        grid = {} # (row, col) -> content
        max_col = 0
        occupied_cells = set() # (row, col)

        # Pre-Scan um Grid aufzubauen
        for r_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
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

        # Grid in Listen umwandeln
        # Annahme: Zeile 0 ist Header (könnte man noch intelligenter machen)
        headers = [grid.get((0, c), "") for c in range(max_col)]
        
        body_rows = []
        for r in range(1, len(rows)):
            row_data = [grid.get((r, c), "") for c in range(max_col)]
            body_rows.append(row_data)

        return MarkdownTable(headers=headers, rows=body_rows)