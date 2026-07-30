# Changelog

## 0.2.1 (2026-07-30)

### Changed
- **Breaking:** the import package was renamed from `table2md` to
  `html_table_rescuer`, matching the distribution name and the renamed GitHub
  repository (`Encephos/html-table-rescuer`). Update imports accordingly:
  `from html_table_rescuer import TableParser`.
- The installed CLI command is now `html-table-rescuer` (was `table2md`).
- The LangChain loader class was renamed from `Table2MDLoader` to
  `HTMLTableRescuerLoader`.

## 0.2.0 (2026-07-30)

### Added
- `table2md` CLI (Typer): file/URL/stdin input, `--format markdown|json|csv`,
  `--strategy`, `--dito-prefix`, `--table`, `--output`, `--no-links`,
  `--no-bold`, `--no-italic`, `--parser`. Piped input works without an
  argument (`curl … | table2md`).
- Public API exports from the package root: `from table2md import TableParser`.
- `py.typed` marker (PEP 561).
- CI workflow (ruff + pytest on Python 3.9 and 3.12).
- Test suite grown from 9 to 50 tests, including the 13 example cases as
  regression tests.

### Fixed
- Invalid `colspan`/`rowspan` values (`""`, `"abc"`, `"0"`, negative) no longer
  crash the parser or silently drop cell content.
- `rowspan` is capped at the last table row (browser behavior); huge values
  like `rowspan="10000"` no longer allocate unbounded grids.
- HTML comments no longer leak into cell output.
- README installation instructions now name the actual PyPI package
  (`html-table-rescuer`).

## 0.1.0 (2025-12-10)

- Initial release: HTML table extraction with rowspan/colspan grid solving,
  Markdown/JSON/CSV export, LangChain document loader.
