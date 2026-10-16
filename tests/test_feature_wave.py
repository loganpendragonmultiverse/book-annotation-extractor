from pathlib import Path

import pytest

from book_annotation_extractor.cli import _load, main
from book_annotation_extractor.core import analyze, render_csv

FIXTURE = Path(__file__).parent / "fixtures" / "My Clippings.txt"


def test_my_clippings_dialect(capsys):
    report = analyze(_load(FIXTURE, "kindle-clippings"))
    assert report["count"] == 3
    rows = {r["kind"]: r for r in report["annotations"]}
    assert rows["highlight"]["work"] == "Synthetic Harbor (A. Example)"
    assert rows["highlight"]["text"] == "The harbor was quiet.\nA bell rang twice."
    assert rows["highlight"]["location"] == "12-13"
    assert rows["highlight"]["created_at"] == "2026-10-15T10:30:00"
    assert rows["note"]["note"] == "Remember the bell.\nCheck the tide."
    assert rows["bookmark"]["location"] == "20"
    assert "Remember the bell." in render_csv(report)
    assert (
        main([str(FIXTURE), "--adapter", "kindle-clippings", "--kind", "note", "--format", "json"])
        == 0
    )
    assert "Remember the bell." in capsys.readouterr().out


@pytest.mark.parametrize(
    "text",
    [
        "Title\nnot metadata\n\nBody\n==========",
        "Title\n- Your Highlight on Location 1 | Added on nonsense\n\nBody\n==========",
        "Title\n- Your Highlight on Location 1 | Added on Thursday, October 15, 2026 10:30:00 AM\nBody\n==========",
        "Title\n- Your Highlight on Location 1 | Added on Thursday, October 15, 2026 10:30:00 AM\n\nBody",
    ],
)
def test_malformed_clippings(tmp_path, text, capsys):
    path = tmp_path / "bad.txt"
    path.write_text(text)
    assert main([str(path), "--adapter", "kindle-clippings"]) == 2
    assert "block 1" in capsys.readouterr().err


@pytest.mark.parametrize(
    "filters", [{"platforms": {"Kobo"}}, {"date_from": "2026-01-01"}, {"date_to": "2025-01-01"}]
)
def test_filter_before_dedup(filters):
    first = {"work": "A", "text": "Same line", "date": "2025-06-01"}
    later = {**first, "date": "2026-02-01" if "date_to" not in filters else "2024-01-01"}
    data = {
        "sources": [
            {"platform": "Kindle", "items": [first]},
            {"platform": "Kobo", "items": [later, later]},
        ]
    }
    report = analyze(data, **filters)
    assert report["count"] == 1
    assert report["annotations"][0]["provenance"]["source_index"] == 2
    assert report["duplicate_count"] == 1


def test_kind_filter_before_dedup():
    data = {
        "sources": [
            {
                "items": [
                    {"work": "A", "text": "Same", "kind": "highlight"},
                    {"work": "A", "text": "Same", "kind": "note"},
                ]
            }
        ]
    }
    assert analyze(data, kind="note")["count"] == 1


def test_clipping_date_and_metadata_edges():
    from book_annotation_extractor.clippings import parse_clippings

    text = FIXTURE.read_text()
    assert parse_clippings("\ufeff" + text.replace("\n", "\r\n"))[0]["location"] == "12-13"
    assert (
        parse_clippings(text.replace("on Location 12-13", "on page 3 | Location 12-13"))[0][
            "location"
        ]
        == "12-13"
    )
    assert parse_clippings(text.replace("10:30:00 AM", "12:30:00 AM"))[0]["created_at"].endswith(
        "T00:30:00"
    )
    assert parse_clippings(text.replace("10:30:00 AM", "12:30:00 PM"))[0]["created_at"].endswith(
        "T12:30:00"
    )
    for value in [
        "",
        "==========",
        text.replace("10:30:00 AM", "13:30:00 AM"),
        text.replace("October 15", "October 99"),
        text.replace("The harbor was quiet.\nA bell rang twice.", ""),
    ]:
        with pytest.raises(ValueError, match="block"):
            parse_clippings(value)
