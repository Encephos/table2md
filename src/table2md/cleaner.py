from bs4 import Tag, NavigableString
from .models import ParseConfig

def clean_cell_content(cell: Tag, config: ParseConfig) -> str:
    """
    Wandelt HTML-Inhalt einer Zelle in Markdown-String um,
    basierend auf der Konfiguration.
    """
    if not cell:
        return ""

    text_parts = []
    
    for content in cell.contents:
        if isinstance(content, NavigableString):
            text = content.strip()
            # Pipes und Newlines sind Gift für MD Tabellen
            text = text.replace("|", "\\|").replace("\n", " ")
            if text:
                text_parts.append(text)
        
        elif isinstance(content, Tag):
            # Rekursive Verarbeitung für Tags im Tag möglich, 
            # hier flach gehalten für Stabilität.
            
            inner_text = content.get_text(strip=True).replace("|", "\\|").replace("\n", " ")
            
            if content.name == 'br':
                text_parts.append("<br>")
            
            elif content.name == 'a' and content.get('href') and config.keep_links:
                href = content.get('href')
                text_parts.append(f"[{inner_text}]({href})")
            
            elif content.name in ['b', 'strong'] and config.keep_bold:
                text_parts.append(f"**{inner_text}**")
            
            elif content.name in ['i', 'em'] and config.keep_italic:
                text_parts.append(f"_{inner_text}_")
            
            else:
                # Standard: Nur Text nehmen, Tag entfernen
                text_parts.append(inner_text)

    return " ".join(text_parts).strip()
