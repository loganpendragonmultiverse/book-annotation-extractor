from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from .core import analyze, render_csv, render_json, render_markdown


def _load(path: Path, adapter: str) -> dict[str, Any]:
    if adapter == "json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise TypeError("JSON input must be an object")
        return value
    if adapter in {"generic-csv", "kobo-csv"}:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        platform = "Kobo" if adapter == "kobo-csv" else "CSV"
        return {"sources": [{"platform": platform, "source": path.name, "items": rows}]}
    text = path.read_text(encoding="utf-8")
    items = []
    for block in text.replace("<br>", "\n").replace("</p>", "\n").split("\n"):
        value = block.strip().removeprefix("<p>").strip()
        if value:
            items.append({"work": path.stem, "text": value})
    return {"sources": [{"platform": "Kindle", "source": path.name, "items": items}]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize exported ebook annotations.")
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--adapter",
        choices=("json", "generic-csv", "kobo-csv", "kindle-text", "kindle-html"),
        default="json",
    )
    parser.add_argument("--format", choices=("markdown", "json", "csv"), default="markdown")
    parser.add_argument("--work", action="append")
    parser.add_argument("--platform", action="append")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--kind", choices=("highlight", "note"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = analyze(
            _load(args.input, args.adapter),
            works=set(args.work or []),
            platforms=set(args.platform or []),
            date_from=args.date_from,
            date_to=args.date_to,
            kind=args.kind,
        )
        rendered = (
            render_json(report)
            if args.format == "json"
            else render_csv(report)
            if args.format == "csv"
            else render_markdown(report)
        )
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
