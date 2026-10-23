# Testing

## 1.2.0 - 2026-10-16

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. Keep regression fixtures synthetic and source inputs unchanged. `tests/test_feature_wave.py` covers the new behavior, malformed inputs and compatibility defaults. Verify README and CHANGELOG in wheel metadata/documentation and in the source archive before release. Protected cross-platform CI and CodeQL remain required; draft PR preparation does not authorize a merge or release.

## 1.2.1 regression and installed acceptance

Run the documented full lint/type/coverage/build commands above. In particular,
`tests/test_gold_review.py` checks malformed fields, null/empty data, inclusive
calendar bounds, literal Markdown and preservation of an existing output.

Install the built wheel in a clean Python environment. From outside this checkout,
run the entire test suite against that installed package; confirm its import path
is in site-packages. Run `annotation-extract` on the installed JSON and synthetic
My Clippings examples in `share/doc/book-annotation-extractor/examples/`, covering
Markdown, JSON, CSV and bounded-date filtering. Repeat after installing the sdist.
Confirm all four authority documents are installed and match the release source.
The existing 90% coverage floor and cross-platform protected CI remain required.

`tests/test_output_links.py` checks refusal of existing dangling-link metadata
on every platform and actual dangling symlinks where creation is supported.

## Preserve repeated annotation occurrences (1.3.0)

Use `annotation-extract input.json --preserve-occurrences --format json` when repeated highlights or notes have locations or source details you want to keep. The same option works with all existing input adapters and with `--format csv` or `--format markdown`.

The opt-in JSON schema is version 3: each unique annotation contains `occurrences`, including the kept occurrence and every duplicate in input order, with platform, work, location, text, note, kind, exported date and source/source-index/item-index provenance. `count` remains the number of unique annotations; `occurrence_count` counts all included occurrences. CSV emits one row per occurrence, adding annotation/occurrence/source/item indices; Markdown displays all occurrence details as literal text. These indices describe this input/report and are not persistent cross-run IDs.

Existing filters apply to each occurrence before grouping. Repeated identical locations remain separate occurrences; bookmark locations and annotation kinds retain their existing identity rules. Text fields retain existing trimming/normalization, and timestamps keep their supplied interpretation: no timezone is inferred. Only documented normalized fields are retained, not arbitrary export metadata or the original raw file bytes.

Without the option, JSON stays version 2 and CSV/Markdown retain their existing shape and deduplication behavior. Source files remain read-only and existing output files are refused. Occurrence details can reveal source filenames and annotation content; review exported reports before sharing.

`tests/test_occurrences.py` covers default-schema parity, repeated locations, case/spacing variants, full provenance/date retention, filter-before-grouping behavior, bookmark/kind identity, literal Markdown, CSV grouping indices, empty input and CLI source/output preservation. Repeat the complete suite and real CLI format checks against separately installed wheel and sdist packages outside the checkout. No native ebook applications or private exports are needed.
