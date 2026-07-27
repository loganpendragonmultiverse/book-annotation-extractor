from __future__ import annotations

import csv
import io
import json
from typing import Any

PROJECT = "book-annotation-extractor"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def analyze(
    data: dict[str, Any],
    *,
    works: set[str] | None = None,
    platforms: set[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    kind: str | None = None,
) -> dict[str, Any]:
    sources = _require(data, "sources")
    if not isinstance(sources, list):
        raise TypeError("sources must be a list")
    normalized: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    seen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for source_index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            raise TypeError(f"source {source_index} must be an object")
        platform = str(source.get("platform", "unknown"))
        source_name = str(source.get("source", source.get("filename", f"source-{source_index}")))
        items = source.get("items", [])
        if not isinstance(items, list):
            raise TypeError(f"source {source_index} items must be a list")
        for item_index, item in enumerate(items, 1):
            if not isinstance(item, dict):
                raise TypeError("annotation items must be objects")
            text = str(item.get("text", item.get("highlight", ""))).strip()
            note = str(item.get("note", "")).strip()
            work = str(item.get("work", item.get("title", ""))).strip()
            if not text and not note:
                continue
            annotation_kind = "note" if note and not text else "highlight"
            key = (
                " ".join(text.casefold().split()),
                " ".join(note.casefold().split()),
                work.casefold(),
            )
            record = {
                "platform": platform,
                "work": work,
                "location": item.get("location", ""),
                "text": text,
                "note": note,
                "kind": annotation_kind,
                "created_at": item.get("created_at", item.get("date")),
                "provenance": {
                    "source": source_name,
                    "source_index": source_index,
                    "item_index": item_index,
                },
            }
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
            created = str(record["created_at"] or "")
            if works and work not in works or platforms and platform not in platforms:
                continue
            if date_from and created < date_from or date_to and created > date_to:
                continue
            if kind and annotation_kind != kind:
                continue
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
        lines.extend([f"## {work or 'Untitled Work'}", ""])
        for item in report["annotations"]:
            if item["work"] == work:
                content = item["text"] or item["note"]
                lines.append(f"- **{item['platform']} / {item['location']}**: {content}")
                if item["text"] and item["note"]:
                    lines.append(f"  - Note: {item['note']}")
        lines.append("")
    if report["duplicates"]:
        lines.extend(["## Duplicate Review", ""])
        lines.extend(
            f"- **{item['work']}**: {item['text'] or item['note']}" for item in report["duplicates"]
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
