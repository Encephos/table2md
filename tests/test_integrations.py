"""Tests für die Framework-Integrationen (LangChain, LlamaIndex).

Beide Frameworks sind optionale Extras — die Tests werden übersprungen,
wenn das jeweilige Paket nicht installiert ist.
"""
import pytest

from html_table_rescuer.models import ParseConfig, RowspanStrategy

TWO_TABLES_HTML = """
<table>
    <tr><th>Name</th><th>Alter</th></tr>
    <tr><td>Max</td><td>25</td></tr>
</table>
<table>
    <tr><th>Stadt</th></tr>
    <tr><td>Berlin</td></tr>
</table>
"""

ROWSPAN_HTML = """
<table>
    <tr><th>Gruppe</th><th>Wert</th></tr>
    <tr><td rowspan="2">A</td><td>1</td></tr>
    <tr><td>2</td></tr>
</table>
"""


@pytest.fixture
def html_file(tmp_path):
    def _write(content=TWO_TABLES_HTML):
        f = tmp_path / "tables.html"
        f.write_text(content, encoding="utf-8")
        return f

    return _write


# --- LangChain ---------------------------------------------------------------


@pytest.fixture
def langchain_loader_cls():
    pytest.importorskip("langchain_core")
    pytest.importorskip("langchain_community")
    from html_table_rescuer.integrations.langchain import HTMLTableRescuerLoader

    return HTMLTableRescuerLoader


def test_langchain_one_document_per_table(langchain_loader_cls, html_file):
    docs = langchain_loader_cls(str(html_file())).load()
    assert len(docs) == 2
    assert "| Max | 25 |" in docs[0].page_content
    assert "| Berlin |" in docs[1].page_content


def test_langchain_metadata(langchain_loader_cls, html_file):
    f = html_file()
    docs = langchain_loader_cls(str(f)).load()
    assert docs[0].metadata == {
        "source": str(f),
        "table_index": 0,
        "parser": "html_table_rescuer",
    }
    assert docs[1].metadata["table_index"] == 1


def test_langchain_passes_config(langchain_loader_cls, html_file):
    config = ParseConfig(rowspan_strategy=RowspanStrategy.REPEAT_VALUE)
    docs = langchain_loader_cls(str(html_file(ROWSPAN_HTML)), config=config).load()
    assert docs[0].page_content.count("A") == 2
    assert "dito" not in docs[0].page_content


def test_langchain_missing_file_raises(langchain_loader_cls):
    with pytest.raises(RuntimeError):
        langchain_loader_cls("/nonexistent/file.html").load()


def test_langchain_no_tables(langchain_loader_cls, html_file):
    docs = langchain_loader_cls(str(html_file("<p>nix</p>"))).load()
    assert docs == []


# --- LlamaIndex --------------------------------------------------------------


@pytest.fixture
def llamaindex_reader_cls():
    pytest.importorskip("llama_index.core")
    from html_table_rescuer.integrations.llamaindex import HTMLTableRescuerReader

    return HTMLTableRescuerReader


def test_llamaindex_one_document_per_table(llamaindex_reader_cls, html_file):
    docs = llamaindex_reader_cls().load_data(html_file())
    assert len(docs) == 2
    assert "| Max | 25 |" in docs[0].text
    assert "| Berlin |" in docs[1].text


def test_llamaindex_metadata(llamaindex_reader_cls, html_file):
    f = html_file()
    docs = llamaindex_reader_cls().load_data(f)
    assert docs[0].metadata == {
        "source": str(f),
        "table_index": 0,
        "parser": "html_table_rescuer",
    }
    assert docs[1].metadata["table_index"] == 1


def test_llamaindex_extra_info_wins(llamaindex_reader_cls, html_file):
    """SimpleDirectoryReader reicht extra_info durch — das muss Vorrang haben."""
    docs = llamaindex_reader_cls().load_data(
        html_file(), extra_info={"file_name": "tables.html", "parser": "custom"}
    )
    assert docs[0].metadata["file_name"] == "tables.html"
    assert docs[0].metadata["parser"] == "custom"
    assert docs[0].metadata["table_index"] == 0


def test_llamaindex_accepts_str_path(llamaindex_reader_cls, html_file):
    docs = llamaindex_reader_cls().load_data(str(html_file()))
    assert len(docs) == 2


def test_llamaindex_passes_config(llamaindex_reader_cls, html_file):
    config = ParseConfig(rowspan_strategy=RowspanStrategy.REPEAT_VALUE)
    docs = llamaindex_reader_cls(config=config).load_data(html_file(ROWSPAN_HTML))
    assert docs[0].text.count("A") == 2
    assert "dito" not in docs[0].text


def test_llamaindex_lazy_load_is_lazy(llamaindex_reader_cls, html_file):
    gen = llamaindex_reader_cls().lazy_load_data(html_file())
    assert next(iter(gen)).metadata["table_index"] == 0


def test_llamaindex_missing_file_raises(llamaindex_reader_cls):
    with pytest.raises(RuntimeError):
        llamaindex_reader_cls().load_data("/nonexistent/file.html")


def test_llamaindex_no_tables(llamaindex_reader_cls, html_file):
    docs = llamaindex_reader_cls().load_data(html_file("<p>nix</p>"))
    assert docs == []
