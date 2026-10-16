"""Parse the documented English Kindle My Clippings text dialect."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

MONTHS = {
    name: i
    for i, name in enumerate(
        (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ),
        1,
    )
}
META = re.compile(
    r"- Your (Highlight|Note|Bookmark) on (?:page [0-9]+ [|] )?"
    r"Location ([0-9]+(?:-[0-9]+)?) [|] Added on (.+)"
)
DATE = re.compile(
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
    r"([A-Za-z]+) ([0-9]{1,2}), ([0-9]{4}) ([0-9]{1,2}):([0-9]{2}):([0-9]{2}) (AM|PM)"
)


def parse_clippings(text: str) -> list[dict[str, Any]]:
    lines = text.lstrip("\ufeff").splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line == "==========":
            blocks.append(current)
            current = []
        else:
            current.append(line)
    if any(line.strip() for line in current):
        raise ValueError(f"Kindle block {len(blocks) + 1}: missing separator")
    items: list[dict[str, Any]] = []
    for index, block in enumerate(blocks, 1):
        while block and not block[0].strip():
            block.pop(0)
        if len(block) < 3 or not block[0].strip() or block[2].strip():
            raise ValueError(f"Kindle block {index}: expected title, metadata and blank line")
        metadata = META.fullmatch(block[1])
        if metadata is None:
            raise ValueError(f"Kindle block {index}: unsupported metadata")
        kind, location, date = metadata.groups()
        parsed = DATE.fullmatch(date)
        try:
            if parsed is None:
                raise ValueError()
            month, day, year, hour, minute, second, period = parsed.groups()
            if not 1 <= int(hour) <= 12:
                raise ValueError()
            created = datetime(
                int(year),
                MONTHS[month],
                int(day),
                int(hour) % 12 + (12 if period == "PM" else 0),
                int(minute),
                int(second),
            ).isoformat()
        except (ValueError, KeyError):
            raise ValueError(f"Kindle block {index}: unsupported or invalid date") from None
        body = "\n".join(block[3:]).strip()
        if kind != "Bookmark" and not body:
            raise ValueError(f"Kindle block {index}: missing annotation body")
        items.append(
            {
                "work": block[0].strip(),
                "kind": kind.lower(),
                "location": location,
                "created_at": created,
                "note" if kind == "Note" else "text": body,
            }
        )
    if not items:
        raise ValueError("Kindle block 1: no clipping blocks")
    return items
