from pathlib import Path

from launchlab.portfolio import END, START, update_readme


def test_readme_update_is_idempotent(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# LaunchLab\n\nExisting content.\n", encoding="utf-8")

    update_readme(readme)
    first = readme.read_text(encoding="utf-8")
    update_readme(readme)
    second = readme.read_text(encoding="utf-8")

    assert first == second
    assert first.count(START) == 1
    assert first.count(END) == 1
    assert "Research question" in first
    assert "Limitations" in first


def test_readme_update_preserves_existing_content(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# LaunchLab\n\nExisting content.\n", encoding="utf-8")

    update_readme(readme)

    updated = readme.read_text(encoding="utf-8")
    assert "Existing content." in updated
