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
