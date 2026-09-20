"""Construção e serialização do manifest do curso (files_manifest.json)."""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path


def get_or_create_course_id(modo_plataforma_dir: Path) -> str:
    """Reaproveita o .course_id existente (não perde progresso salvo) ou cria um novo."""
    course_id_file = modo_plataforma_dir / ".course_id"
    if course_id_file.exists():
        existing = course_id_file.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    return uuid.uuid4().hex


def write_course_id(modo_plataforma_dir: Path, course_id: str) -> None:
    (modo_plataforma_dir / ".course_id").write_text(course_id, encoding="utf-8")


def make_file_id(relative_path: str) -> str:
    """Id determinístico por path relativo — regenerar o curso não perde notas/progresso."""
    return hashlib.md5(relative_path.encode("utf-8")).hexdigest()


def build_manifest(course_name: str, modules: list[dict]) -> dict:
    return {
        "name": course_name,
        "modules": modules,
    }


def to_json(manifest: dict, *, compact: bool = False) -> str:
    if compact:
        return json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(manifest, ensure_ascii=False, indent=2)
