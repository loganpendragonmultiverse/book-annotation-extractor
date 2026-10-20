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
