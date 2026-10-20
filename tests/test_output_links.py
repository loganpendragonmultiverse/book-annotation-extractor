from pathlib import Path

import pytest

from book_annotation_extractor.cli import main

SOURCE = Path(__file__).parents[1] / "examples" / "sample.json"
EXTRA = []


def test_existing_link_metadata_refused_before_open(tmp_path, monkeypatch, capsys):
    output = tmp_path / "report.md"
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda self: self == output or original(self))
    assert main([str(SOURCE), "--output", str(output)] + EXTRA) == 2
    assert "already exists" in capsys.readouterr().err
    assert not output.exists()


def test_actual_dangling_symlink_does_not_create_target(tmp_path):
    target = tmp_path / "absent.md"
    output = tmp_path / "report.md"
    try:
        output.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    assert main([str(SOURCE), "--output", str(output)] + EXTRA) == 2
    assert output.is_symlink() and not target.exists()
