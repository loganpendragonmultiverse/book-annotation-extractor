import copy
import csv
import io
import json
from typing import Any

import pytest

from book_annotation_extractor.cli import main
from book_annotation_extractor.core import analyze, render_csv, render_json, render_markdown


def sample() -> dict[str, Any]:
    return {
        "sources": [
            {
                "platform": "Kobo",
                "source": "first.csv",
                "items": [
                    {
                        "work": "Example",
                        "text": "Shared   TEXT",
                        "note": "Same note",
                        "location": "10",
                        "created_at": "2026-10-01T12:00:00",
                    }
                ],
            },
            {
                "platform": "Kindle",
                "source": "second.txt",
                "items": [
                    {
                        "work": "Example",
                        "text": "shared text",
                        "note": "same NOTE",
                        "location": "40-42",
                        "created_at": "2026-10-02T01:00:00+03:00",
                    },
                    {
                        "work": "Example",
                        "text": "SHARED TEXT",
                        "note": "Same note",
                        "location": "40-42",
                        "created_at": None,
                    },
                ],
            },
        ]
    }


def test_default_schema_and_exports_stay_compatible() -> None:
    report = analyze(sample())
    assert report == analyze(sample(), preserve_occurrences=False)
    assert set(report) == {
        "version",
        "project",
        "annotations",
        "count",
        "platforms",
        "duplicates",
        "duplicate_count",
    }
    assert report["version"] == 2
    assert report["count"] == 1 and report["duplicate_count"] == 2
    assert report["platforms"] == ["Kobo"]
    assert "occurrences" not in report["annotations"][0]
    rows = list(csv.DictReader(io.StringIO(render_csv(report))))
    assert len(rows) == 1
    assert list(rows[0]) == [
        "platform",
        "work",
        "location",
        "kind",
        "text",
        "note",
        "created_at",
        "source",
    ]
    assert "Occurrence 1" not in render_markdown(report)


def test_preserves_every_occurrence_without_mutating_input() -> None:
    data = sample()
    before = copy.deepcopy(data)
    report = analyze(data, preserve_occurrences=True)
    assert data == before
    assert report["version"] == 3
    assert (
        report["count"] == 1 and report["duplicate_count"] == 2 and report["occurrence_count"] == 3
    )
    assert report["platforms"] == ["Kindle", "Kobo"]
    occurrences = report["annotations"][0]["occurrences"]
    assert [x["location"] for x in occurrences] == ["10", "40-42", "40-42"]
    assert [x["text"] for x in occurrences] == ["Shared   TEXT", "shared text", "SHARED TEXT"]
    assert [x["created_at"] for x in occurrences] == [
        "2026-10-01T12:00:00",
        "2026-10-02T01:00:00+03:00",
        None,
    ]
    assert [x["provenance"] for x in occurrences] == [
        {"source": "first.csv", "source_index": 1, "item_index": 1},
        {"source": "second.txt", "source_index": 2, "item_index": 1},
        {"source": "second.txt", "source_index": 2, "item_index": 2},
    ]
    assert json.loads(render_json(report)) == report


def test_csv_has_one_row_per_occurrence_with_group_and_source_indices() -> None:
    report = analyze(sample(), preserve_occurrences=True)
    rows = list(csv.DictReader(io.StringIO(render_csv(report))))
    assert len(rows) == 3
    assert [x["annotation_index"] for x in rows] == ["1", "1", "1"]
    assert [x["occurrence_index"] for x in rows] == ["1", "2", "3"]
    assert [x["source_index"] for x in rows] == ["1", "2", "2"]
    assert [x["item_index"] for x in rows] == ["1", "1", "2"]
    assert [x["source"] for x in rows] == ["first.csv", "second.txt", "second.txt"]
    assert rows[2]["created_at"] == ""
    assert [x["location"] for x in rows] == ["10", "40-42", "40-42"]


def test_markdown_displays_literal_occurrence_details() -> None:
    data = sample()
    data["sources"][1]["source"] = "[source](https://example.invalid) <tag>"
    report = analyze(data, preserve_occurrences=True)
    text = render_markdown(report)
    assert "Occurrence 1" in text and "Occurrence 3" in text
    assert "source 2, item 2" in text
    assert r"2026\-10\-02T01:00:00\+03:00" in text
    assert "not supplied" in text
    assert "\\[source\\]" in text and "&lt;tag&gt;" in text
    assert "<tag>" not in text
    assert "SHARED TEXT" in text


def test_filters_apply_before_occurrence_grouping() -> None:
    report = analyze(sample(), preserve_occurrences=True, platforms={"Kindle"})
    assert report["count"] == 1 and report["occurrence_count"] == 2
    assert report["platforms"] == ["Kindle"]
    assert report["annotations"][0]["occurrences"][0]["provenance"]["source_index"] == 2
    dated = analyze(sample(), preserve_occurrences=True, date_from="2026-10-02")
    assert dated["occurrence_count"] == 1 and dated["duplicate_count"] == 0
    assert dated["annotations"][0]["location"] == "40-42"
    assert analyze(sample(), preserve_occurrences=True, works={"Other"})["occurrence_count"] == 0


def test_bookmarks_and_kinds_keep_existing_identity_rules() -> None:
    data = {
        "sources": [
            {
                "platform": "P",
                "items": [
                    {"work": "W", "kind": "bookmark", "location": "1"},
                    {"work": "W", "kind": "bookmark", "location": "2"},
                    {"work": "W", "kind": "bookmark", "location": "1"},
                    {"work": "W", "kind": "note", "text": "x"},
                    {"work": "W", "kind": "highlight", "text": "x"},
                ],
            }
        ]
    }
    report = analyze(data, preserve_occurrences=True)
    assert (
        report["count"] == 4 and report["occurrence_count"] == 5 and report["duplicate_count"] == 1
    )
    assert sorted(len(x["occurrences"]) for x in report["annotations"]) == [1, 1, 1, 2]
    markdown = render_markdown(report)
    assert "kind: bookmark" in markdown
    assert "kind: note" in markdown
    assert "kind: highlight" in markdown


def test_empty_and_identical_repeated_occurrences() -> None:
    empty = analyze({"sources": []}, preserve_occurrences=True)
    assert empty["occurrence_count"] == 0
    assert len(render_csv(empty).splitlines()) == 1
    data = {"sources": [{"items": [{"work": "W", "text": "x", "location": "1"}] * 3}]}
    report = analyze(data, preserve_occurrences=True)
    assert report["occurrence_count"] == 3
    assert [x["provenance"]["item_index"] for x in report["annotations"][0]["occurrences"]] == [
        1,
        2,
        3,
    ]


def test_requires_boolean_mode() -> None:
    value: Any = "yes"
    with pytest.raises(TypeError, match="boolean"):
        analyze(sample(), preserve_occurrences=value)


@pytest.mark.parametrize("format_name", ["json", "csv", "markdown"])
def test_cli_opt_in_and_source_preservation(tmp_path: Any, capsys: Any, format_name: str) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    before = source.read_bytes()
    assert main([str(source), "--preserve-occurrences", "--format", format_name]) == 0
    output = capsys.readouterr().out
    if format_name == "json":
        assert json.loads(output)["occurrence_count"] == 3
    elif format_name == "csv":
        assert len(list(csv.DictReader(io.StringIO(output)))) == 3
    else:
        assert "Occurrence 3" in output
    assert source.read_bytes() == before
    existing = tmp_path / "existing.txt"
    existing.write_text("keep", encoding="utf-8")
    assert main([str(source), "--preserve-occurrences", "--output", str(existing)]) == 2
    assert existing.read_text(encoding="utf-8") == "keep"
