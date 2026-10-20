import json

import pytest

from book_annotation_extractor.cli import main
from book_annotation_extractor.core import analyze, render_markdown


def data(**fields):
    return {"sources": [{"platform": "Kobo", "items": [{"text": "Hello", **fields}]}]}


@pytest.mark.parametrize(
    "field", ["text", "highlight", "note", "work", "title", "location", "kind", "created_at"]
)
@pytest.mark.parametrize("value", [False, 12, [], {}])
def test_typed_fields(field, value):
    with pytest.raises((TypeError, ValueError)):
        analyze(data(**{field: value}))


def test_null_text_rejected_but_null_date_allowed():
    with pytest.raises(TypeError):
        analyze(data(text=None))
    assert analyze(data(created_at=None))["count"] == 1
    assert analyze(data(created_at=None), date_to="2026-10-20")["count"] == 0


@pytest.mark.parametrize("field", ["platform", "source", "filename"])
def test_source_fields(field):
    with pytest.raises(TypeError):
        analyze({"sources": [{field: [], "items": []}]})


def test_calendar_date_bounds():
    payload = data(created_at="2026-10-20T23:59:59")
    assert analyze(payload, date_from="2026-10-20", date_to="2026-10-20")["count"] == 1
    assert analyze(payload, date_from="2026-10-21")["count"] == 0
    assert analyze(payload, date_to="2026-10-19")["count"] == 0
    for kwargs in [
        {"date_from": "2026-02-30"},
        {"date_to": "2026-1-1"},
        {"date_from": "2026-10-21", "date_to": "2026-10-20"},
    ]:
        with pytest.raises(ValueError):
            analyze(payload, **kwargs)
    with pytest.raises(ValueError):
        analyze(data(created_at="not a date"), date_to="2026-10-20")


def test_markup_is_literal_and_multiline_preserved():
    payload = data(
        work="<script>x</script>", text="[click](javascript:bad)\nnext", note="**not bold**"
    )
    payload["sources"][0]["items"].append(payload["sources"][0]["items"][0].copy())
    result = render_markdown(analyze(payload))
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "\\[click\\]" in result
    assert "<br>next" in result
    assert "**not bold**" not in result
    assert "Duplicate Review" in result


def test_report_existing_file_is_preserved(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data()))
    output = tmp_path / "report.md"
    output.write_text("valuable")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.read_text() == "valuable"
    assert "error:" in capsys.readouterr().err


def test_empty_sources_and_bad_root():
    assert analyze({"sources": []})["count"] == 0
    with pytest.raises(TypeError):
        analyze([])
    with pytest.raises(ValueError):
        analyze(data(), kind="unknown")
