from __future__ import annotations

import json
from typing import Any

PROJECT = "book-annotation-extractor"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _annotations(data: dict[str, Any]) -> dict[str, Any]:
    normalized = []
    seen = set()
    for source in _require(data, "sources"):
        platform = str(source.get("platform", "unknown"))
        for item in source.get("items", []):
            text = str(item.get("text", "")).strip()
            note = str(item.get("note", "")).strip()
            key = (text.casefold(), note.casefold(), str(item.get("work", "")).casefold())
            if not text or key in seen:
                continue
            seen.add(key)
            normalized.append(
                {
                    "platform": platform,
                    "work": item.get("work", ""),
                    "location": item.get("location", ""),
                    "text": text,
                    "note": note,
                    "created_at": item.get("created_at"),
                }
            )
    normalized.sort(
        key=lambda item: (
            str(item["work"]).casefold(),
            str(item["location"]),
            str(item["created_at"] or ""),
        )
    )
    return {
        "annotations": normalized,
        "count": len(normalized),
        "platforms": sorted({item["platform"] for item in normalized}),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_annotations(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
