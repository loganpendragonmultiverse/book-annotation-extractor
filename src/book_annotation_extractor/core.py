from __future__ import annotations

import csv
import html
import io
import json
import re
from datetime import date
from typing import Any

PROJECT = "book-annotation-extractor"


def _text(data: dict[str, Any], key: str, fallback: str = "") -> str:
    value = data.get(key, fallback)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value.strip()


def _boundary(value: str | None, name: str) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError(f"{name} must be a YYYY-MM-DD calendar date")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{name} must be a valid YYYY-MM-DD calendar date") from None


def _markdown(value: str) -> str:
    escaped = html.escape(value, quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>-])", r"\\\1", escaped).replace("\n", "<br>")


def analyze(
    data: dict[str, Any],
    *,
    works: set[str] | None = None,
    platforms: set[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    kind: str | None = None,
) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TypeError("input must be an object")
    if "sources" not in data or data["sources"] is None:
        raise ValueError("sources is required")
    sources = data["sources"]
    lower = _boundary(date_from, "date_from")
    upper = _boundary(date_to, "date_to")
    if lower and upper and lower > upper:
        raise ValueError("date_from must not be after date_to")
    if kind is not None and kind not in {"highlight", "note", "bookmark"}:
        raise ValueError("annotation kind must be highlight, note, or bookmark")
    if not isinstance(sources, list):
        raise TypeError("sources must be a list")
    normalized: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    seen: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for source_index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            raise TypeError(f"source {source_index} must be an object")
        platform = _text(source, "platform", "unknown")
        source_name = _text(source, "source", _text(source, "filename", f"source-{source_index}"))
        items = source.get("items", [])
        if not isinstance(items, list):
            raise TypeError(f"source {source_index} items must be a list")
        for item_index, item in enumerate(items, 1):
            if not isinstance(item, dict):
                raise TypeError("annotation items must be objects")
            text = _text(item, "text", _text(item, "highlight"))
            note = _text(item, "note")
            work = _text(item, "work", _text(item, "title"))
            annotation_kind = item.get("kind", "note" if note and not text else "highlight")
            if not isinstance(annotation_kind, str) or annotation_kind not in {
                "highlight",
                "note",
                "bookmark",
            }:
                raise ValueError("annotation kind must be highlight, note, or bookmark")
            location = _text(item, "location")
            created_at = item.get("created_at", item.get("date"))
            if created_at is not None and not isinstance(created_at, str):
                raise TypeError("created_at must be a string or null")
            if not text and not note and annotation_kind != "bookmark":
                continue
            key = (
                " ".join(text.casefold().split()),
                " ".join(note.casefold().split()),
                work.casefold(),
                annotation_kind,
                location if annotation_kind == "bookmark" else "",
            )
            record = {
                "platform": platform,
                "work": work,
                "location": location,
                "text": text,
                "note": note,
                "kind": annotation_kind,
                "created_at": created_at,
                "provenance": {
                    "source": source_name,
                    "source_index": source_index,
                    "item_index": item_index,
                },
            }
            created = str(record["created_at"] or "")
            if works and work not in works or platforms and platform not in platforms:
                continue
            if lower or upper:
                # Compare the exported local calendar day; never invent a timezone.
                created_day = _boundary(created[:10], "annotation date") if created else None
                if created_day is None:
                    continue
                if lower and created_day < lower or upper and created_day > upper:
                    continue
            if kind and annotation_kind != kind:
                continue
            if key in seen:
                duplicates.append(
                    {
                        "kept": seen[key]["provenance"],
                        "duplicate": record["provenance"],
                        "work": work,
                        "text": text,
                        "note": note,
                    }
                )
                continue
            seen[key] = record
            normalized.append(record)
    normalized.sort(
        key=lambda item: (
            item["work"].casefold(),
            str(item["location"]),
            str(item["created_at"] or ""),
        )
    )
    return {
        "version": 2,
        "project": PROJECT,
        "annotations": normalized,
        "count": len(normalized),
        "platforms": sorted({item["platform"] for item in normalized}),
        "duplicates": duplicates,
        "duplicate_count": len(duplicates),
    }


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Book Annotation Extractor",
        "",
        f"Annotations: **{report['count']}** - Duplicate candidates: **{report['duplicate_count']}**",
        "",
    ]
    works = sorted({item["work"] for item in report["annotations"]}, key=str.casefold)
    for work in works:
        lines.extend([f"## {_markdown(work or 'Untitled Work')}", ""])
        for item in report["annotations"]:
            if item["work"] == work:
                content = item["text"] or item["note"]
                lines.append(
                    f"- **{_markdown(item['platform'])} / {_markdown(item['location'])}**: {_markdown(content)}"
                )
                if item["text"] and item["note"]:
                    lines.append(f"  - Note: {_markdown(item['note'])}")
        lines.append("")
    if report["duplicates"]:
        lines.extend(["## Duplicate Review", ""])
        lines.extend(
            f"- **{_markdown(item['work'])}**: {_markdown(item['text'] or item['note'])}"
            for item in report["duplicates"]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_csv(report: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    fields = ["platform", "work", "location", "kind", "text", "note", "created_at", "source"]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for item in report["annotations"]:
        writer.writerow(
            {**{key: item.get(key, "") for key in fields}, "source": item["provenance"]["source"]}
        )
    return output.getvalue()
