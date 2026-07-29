from typing import List, Optional, Iterator
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from table2md.core import TableParser
from table2md.models import ParseConfig

class Table2MDLoader(BaseLoader):
    """
    LangChain Document Loader der HTML-Dateien nach Tabellen durchsucht 
    und diese als Markdown-Dokumente extrahiert. Behebt typische Probleme 
    mit colspan und rowspan.
    """

    def __init__(self, file_path: str, config: Optional[ParseConfig] = None):
        """
        Initialisiert den Loader.

        Args:
            file_path: Pfad zur HTML-Datei.
            config: Optionales table2md ParseConfig Objekt.
        """
        self.file_path = file_path
        self.config = config

    def lazy_load(self) -> Iterator[Document]:
        """Lädt die HTML-Datei und yieldet jede Tabelle als eigenes LangChain Document."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except Exception as e:
            raise RuntimeError(f"Error reading file {self.file_path}: {e}")

        parser = TableParser(html_content, self.config)
        tables = parser.parse()

        for idx, table in enumerate(tables):
            # Nutzt jetzt die sauber umbenannte to_markdown() Methode
            md_content = table.to_markdown()
            
            metadata = {
                "source": self.file_path,
                "table_index": idx,
                "parser": "table2md"
            }
            
            yield Document(page_content=md_content, metadata=metadata)
