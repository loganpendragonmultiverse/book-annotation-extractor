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
