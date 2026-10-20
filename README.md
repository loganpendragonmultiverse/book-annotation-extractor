# Book Annotation Extractor

[![CI](https://github.com/loganpendragonmultiverse/book-annotation-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/book-annotation-extractor/actions/workflows/ci.yml)

Normalize exported highlights and notes from multiple ebook platforms into portable records. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Three-minute start

```bash
python -m pip install .
annotation-extract examples/sample.json
annotation-extract examples/sample.json --format json --output report.json
annotation-extract kobo.csv --adapter kobo-csv --format csv --output annotations.csv
```

The example documents the v1 input shape. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

Version 1.1 reads the original JSON format plus exported Kindle text/HTML, Kobo CSV, and generic CSV files. Every normalized item includes source provenance. Repeated `--work` and `--platform` filters, date bounds, and `--kind highlight|note` narrow a report. Markdown groups annotations by work, CSV provides a portable table, and duplicate candidates remain visible for review.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

The tool only normalizes files the user has already exported. It does not bypass DRM, log into platforms, or recover unavailable annotations.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

Release metadata must stay aligned across the package, changelog, GitHub release, and Logan Pendragon Forge catalog.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## 1.2.0 - 2026-10-16

Use `annotation-extract "My Clippings.txt" --adapter kindle-clippings --format json` for the supported English Kindle My Clippings text dialect. Each block has a title line (preserved verbatim, including an author in parentheses), `- Your Highlight on Location 12-13 | Added on Thursday, October 15, 2026 10:30:00 AM`, a blank line, multiline body, and a line containing exactly `==========`. `Note` and empty-body `Bookmark` blocks are supported, as is `on page 3 | Location 12-13` metadata. Dates become local ISO timestamps without an invented timezone. Note bodies populate `note`; highlights populate `text`; bookmarks retain their location and type. Malformed blocks fail the import with a numbered diagnostic instead of becoming annotations. The tests/fixtures/My Clippings.txt file is wholly synthetic. Other languages, date layouts and HTML exports are outside this dialect.

`kindle-text` and `kindle-html` retain their legacy line-based behavior for compatibility; they do not parse My Clippings metadata or general HTML. JSON, Kobo/generic CSV and JSON/CSV report output remain supported. Work/platform/date/kind filtering now precedes deduplication, and duplicate review includes only eligible records. `--kind bookmark` selects bookmarks. This tool uses exported local files only, with no DRM access, login or network calls.

## Typed input and inclusive date filters (1.2.1)

Annotation text, notes, titles, platform, source and location fields must be strings.
Malformed values fail clearly instead of becoming invented annotation text.
An empty source list produces an empty report; missing sources remain an error.
Dates may be null when no date filter is requested. Bounds use valid `YYYY-MM-DD`
calendar dates and include the entire exported local day at both ends:

```bash
annotation-extract "My Clippings.txt" --adapter kindle-clippings --date-from 2026-10-15 --date-to 2026-10-15
```

Undated annotations are excluded when a bound is present. Reversed or malformed
bounds fail clearly. Markdown displays supplied markup literally and preserves
multiline annotations. JSON and CSV preserve validated, normalized text.
Existing report files are protected by exclusive creation.

The installed wheel includes all four project documents and examples under
`share/doc/book-annotation-extractor/` inside the Python environment. Use
`python -c "import sys; print(sys.prefix)"` to locate that environment. Run the
installed `annotation-extract` command against the packaged `examples/sample.json`
or the synthetic `examples/My Clippings.txt` without needing a source checkout.

CSV imports require nonempty, unique headers and the same number of cells in
every nonblank record. Quoted commas and multiline fields remain supported.
Ambiguous or malformed CSV fails before report generation instead of discarding
an earlier column or inventing a missing cell.

Existing output paths, including dangling symbolic links, are refused before
exclusive file creation. This protects ordinary output collisions; it does not
promise protection against hostile concurrent file-system changes.
