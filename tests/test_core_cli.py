import json
from pathlib import Path

import pytest

from book_annotation_extractor.cli import main
from book_annotation_extractor.core import (
    PROJECT,
    analyze,
    render_csv,
    render_json,
    render_markdown,
)


def test_representative_sample_has_expected_result():
    data = json.loads(
        (Path(__file__).parents[1] / "examples" / "sample.json").read_text(encoding="utf-8")
    )
    report = analyze(data)
    assert report["version"] == 2 and report["project"] == PROJECT
    assert report["count"] == 2 and report["platforms"] == ["Kindle", "Kobo"]
    assert report["duplicate_count"] == 1 and "Duplicate Review" in render_markdown(report)
    assert render_csv(report).startswith("platform,work")
    assert f'"project": "{PROJECT}"' in render_json(report)
    assert PROJECT.replace("-", " ").title() in render_markdown(report)


def test_missing_required_input_is_rejected():
    with pytest.raises(ValueError):
        analyze({})


def test_cli_json_and_output_safety(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    assert main([str(source), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["project"] == PROJECT
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2


def test_csv_adapter_and_filters(tmp_path, capsys):
    source = tmp_path / "annotations.csv"
    source.write_text(
        "work,location,text,note,created_at\nHarbor,4,Line,,2026-01-02\n", encoding="utf-8"
    )
    assert (
        main(
            [
                str(source),
                "--adapter",
                "generic-csv",
                "--format",
                "csv",
                "--work",
                "Harbor",
                "--date-from",
                "2026-01-01",
            ]
        )
        == 0
    )
    assert "Harbor" in capsys.readouterr().out
    report = analyze(
        {
            "sources": [
                {"platform": "Kobo", "items": [{"work": "A", "note": "N", "date": "2026-01-01"}]}
            ]
        },
        kind="note",
    )
    assert report["annotations"][0]["kind"] == "note"


def test_more_adapters_filters_and_errors(tmp_path, capsys):
    kindle = tmp_path / "Harbor.txt"
    kindle.write_text("First line\nSecond line\n", encoding="utf-8")
    assert main([str(kindle), "--adapter", "kindle-text", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["count"] == 2
    kobo = tmp_path / "kobo.csv"
    kobo.write_text("title,location,highlight,date\nHarbor,5,Wave,2026-02-01\n", encoding="utf-8")
    assert main([str(kobo), "--adapter", "kobo-csv", "--platform", "Kobo"]) == 0
    assert "Wave" in capsys.readouterr().out
    data = {
        "sources": [
            {
                "platform": "Kindle",
                "source": "x",
                "items": [
                    {"work": "A", "text": "Old", "created_at": "2025-01-01"},
                    {"work": "B", "text": "New", "created_at": "2026-02-01"},
                ],
            }
        ]
    }
    assert (
        analyze(
            data, works={"B"}, platforms={"Kindle"}, date_from="2026-01-01", date_to="2026-12-31"
        )["count"]
        == 1
    )
    with pytest.raises(TypeError, match="sources"):
        analyze({"sources": {}})
    with pytest.raises(TypeError, match="source 1"):
        analyze({"sources": ["bad"]})
    with pytest.raises(TypeError, match="items"):
        analyze({"sources": [{"items": {}}]})
