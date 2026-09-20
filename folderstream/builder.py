"""Monta a pasta 'FolderStream' a partir do manifest do curso (todos os temas embutidos)."""
from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from . import manifest as manifest_mod

BASE_DIR = Path(__file__).resolve().parent
THEMES_DIR = BASE_DIR / "themes"
TEMPLATE_DIR = BASE_DIR / "template"

THEME_FILES = [
    "base.css",
    "light_A.css",
    "light_B.css",
    "dark_A.css",
    "dark_B.css",
    "blue_A.css",
    "blue_B.css",
    "orange_A.css",
    "orange_B.css",
]


def _build_style_css() -> str:
    parts = []
    for filename in THEME_FILES:
        parts.append((THEMES_DIR / filename).read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def _build_script_js(course_id: str, course_json_compact: str) -> str:
    template = (TEMPLATE_DIR / "player.js").read_text(encoding="utf-8")
    template = template.replace("__COURSE_ID__", course_id)
    template = template.replace("__COURSE_DATA__", course_json_compact)
    return template


def _render_index_html(course_title: str, logo_file: str | None) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    template = env.get_template("index.html.j2")
    return template.render(course_title=course_title, logo_file=logo_file)


def generate_batch_index(parent_path: Path, entries: list[tuple[str, Path]]) -> Path:
    """Gera 'Indice de Cursos.html' na pasta-mãe, com links para cada curso já gerado."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
    template = env.get_template("index_batch.html.j2")

    courses = []
    for display_name, modo_plataforma_dir in entries:
        href = (modo_plataforma_dir / "index.html").resolve().relative_to(parent_path.resolve()).as_posix()
        courses.append({"name": display_name, "folder": modo_plataforma_dir.parent.name, "href": href})
    courses.sort(key=lambda c: c["name"].lower())

    html = template.render(courses=courses)
    out_path = parent_path / "Indice de Cursos.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def generate(
    course_root: Path,
    modules: list[dict],
    modo_plataforma_dir: Path,
    *,
    course_name: str | None = None,
    logo_path: Path | None = None,
    force: bool = False,
) -> Path:
    if modo_plataforma_dir.exists() and not force:
        raise FileExistsError(
            f"'{modo_plataforma_dir}' já existe. Use --force para regenerar."
        )

    display_name = course_name or course_root.name
    course_id = manifest_mod.get_or_create_course_id(modo_plataforma_dir)

    modo_plataforma_dir.mkdir(parents=True, exist_ok=True)

    logo_file_ref = None
    if logo_path is not None:
        assets_dir = modo_plataforma_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        dest = assets_dir / f"logo{logo_path.suffix.lower()}"
        shutil.copyfile(logo_path, dest)
        logo_file_ref = f"assets/{dest.name}"

    course_manifest = manifest_mod.build_manifest(display_name, modules)
    manifest_json_pretty = manifest_mod.to_json(course_manifest)
    manifest_json_compact = manifest_mod.to_json(course_manifest, compact=True)

    (modo_plataforma_dir / "files_manifest.json").write_text(manifest_json_pretty, encoding="utf-8")
    manifest_mod.write_course_id(modo_plataforma_dir, course_id)
    (modo_plataforma_dir / "style.css").write_text(_build_style_css(), encoding="utf-8")
    (modo_plataforma_dir / "script.js").write_text(
        _build_script_js(course_id, manifest_json_compact), encoding="utf-8"
    )
    (modo_plataforma_dir / "index.html").write_text(
        _render_index_html(display_name, logo_file_ref), encoding="utf-8"
    )

    return modo_plataforma_dir
