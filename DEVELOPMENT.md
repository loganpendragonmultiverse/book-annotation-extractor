# Development contract

Normalize exported highlights and notes from multiple ebook platforms into portable records.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, changelog, README claims, repository metadata, release assets, and the Forge catalog together.

## 1.2.0 - 2026-10-16

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. Keep regression fixtures synthetic and source inputs unchanged. `tests/test_feature_wave.py` covers the new behavior, malformed inputs and compatibility defaults. Verify README and CHANGELOG in wheel metadata/documentation and in the source archive before release. Protected cross-platform CI and CodeQL remain required; draft PR preparation does not authorize a merge or release.

## Input and release boundaries

Keep typed fields explicit, preserve the documented local-calendar interpretation
of date bounds, and keep source files read-only. Markdown must display supplied
markup literally; file outputs must use exclusive creation. Empty source lists
are valid while missing sources remain errors. The wheel must contain README,
CHANGELOG, DEVELOPMENT, TESTING, JSON sample and the synthetic My Clippings sample.
A release requires full source and installed wheel/sdist acceptance, independent
review, protected PR/main/tag checks, verified release assets and matching Forge
information pages. Do not infer Gold from a source push alone.

## Preserve repeated annotation occurrences (1.3.0)

Use `annotation-extract input.json --preserve-occurrences --format json` when repeated highlights or notes have locations or source details you want to keep. The same option works with all existing input adapters and with `--format csv` or `--format markdown`.

The opt-in JSON schema is version 3: each unique annotation contains `occurrences`, including the kept occurrence and every duplicate in input order, with platform, work, location, text, note, kind, exported date and source/source-index/item-index provenance. `count` remains the number of unique annotations; `occurrence_count` counts all included occurrences. CSV emits one row per occurrence, adding annotation/occurrence/source/item indices; Markdown displays all occurrence details as literal text. These indices describe this input/report and are not persistent cross-run IDs.

Existing filters apply to each occurrence before grouping. Repeated identical locations remain separate occurrences; bookmark locations and annotation kinds retain their existing identity rules. Text fields retain existing trimming/normalization, and timestamps keep their supplied interpretation: no timezone is inferred. Only documented normalized fields are retained, not arbitrary export metadata or the original raw file bytes.

Without the option, JSON stays version 2 and CSV/Markdown retain their existing shape and deduplication behavior. Source files remain read-only and existing output files are refused. Occurrence details can reveal source filenames and annotation content; review exported reports before sharing.
