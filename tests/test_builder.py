from pathlib import Path

import pytest

from folderstream import builder, scanner


def _make_course(root: Path) -> Path:
    lesson = root / "001. Modulo" / "001. Aula"
    lesson.mkdir(parents=True)
    (lesson / "Aula.mp4").write_bytes(b"")
    return root


@pytest.fixture(autouse=True)
def no_real_ffprobe(monkeypatch):
    monkeypatch.setattr(scanner, "_ffprobe_available", lambda: True)
    monkeypatch.setattr(scanner, "_get_video_duration_ffprobe", lambda path: 42.0)


def test_packaged_assets_exist():
    assert (builder.TEMPLATE_DIR / "player.js").is_file()
    assert (builder.TEMPLATE_DIR / "index.html.j2").is_file()
    assert (builder.TEMPLATE_DIR / "index_batch.html.j2").is_file()
    for filename in builder.THEME_FILES:
        assert (builder.THEMES_DIR / filename).is_file(), filename


def test_generate_writes_self_contained_output(tmp_path):
    course = _make_course(tmp_path / "Meu Curso")
    modules, out_dir, _ = scanner.scan_course(course)

    builder.generate(course, modules, out_dir, course_name=None, logo_path=None, force=False)

    for name in ("index.html", "script.js", "style.css", "files_manifest.json", ".course_id"):
        assert (out_dir / name).is_file(), name
    assert "__COURSE_" not in (out_dir / "script.js").read_text(encoding="utf-8")
    css = (out_dir / "style.css").read_text(encoding="utf-8")
    assert css.count('[data-theme="') >= 8


def test_generate_refuses_existing_output_without_force(tmp_path):
    course = _make_course(tmp_path / "Curso")
    modules, out_dir, _ = scanner.scan_course(course)
    builder.generate(course, modules, out_dir, course_name=None, logo_path=None, force=False)

    with pytest.raises(FileExistsError):
        builder.generate(course, modules, out_dir, course_name=None, logo_path=None, force=False)
