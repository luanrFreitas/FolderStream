"""CLI: gera o 'FolderStream' (player web local) para uma pasta de curso.

Uso:
    folderstream "D:\\Downloads\\Estudo\\Meu Curso"
    folderstream "D:\\Downloads\\Estudo" --batch
    folderstream "D:\\Downloads\\Estudo\\Meu Curso" --force --logo capa.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import builder, scanner


def _count_files(modules: list[dict]) -> int:
    count = 0

    def walk(lessons):
        nonlocal count
        for lesson in lessons:
            count += len(lesson.get("files", []))
            walk(lesson.get("lessons", []))

    for mod in modules:
        walk(mod.get("lessons", []))
    return count


def generate_for_course(course_path: Path, *, force: bool, logo: Path | None, nome: str | None) -> bool:
    if not course_path.is_dir():
        print(f"[erro] pasta não encontrada: {course_path}")
        return False

    print(f"Analisando: {course_path.name}")
    modules, modo_plataforma_dir, duration_cache = scanner.scan_course(course_path)
    total_files = _count_files(modules)

    if total_files == 0:
        print(f"  [aviso] nenhum arquivo encontrado em '{course_path.name}', pulando.")
        return False

    try:
        builder.generate(
            course_path,
            modules,
            modo_plataforma_dir,
            course_name=nome,
            logo_path=logo,
            force=force,
        )
    except FileExistsError as e:
        print(f"  [aviso] {e}")
        return False

    scanner.write_duration_cache(modo_plataforma_dir, duration_cache)
    print(f"  OK -> {modo_plataforma_dir}  ({total_files} arquivos)")
    return True


def run_batch(parent_path: Path, *, force: bool) -> None:
    candidates = sorted(
        (p for p in parent_path.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: p.name.lower(),
    )
    if not candidates:
        print("Nenhuma subpasta de curso encontrada.")
        return

    gerados = 0
    indexed: list[tuple[str, Path]] = []
    for course_dir in candidates:
        if course_dir.name == scanner.OUTPUT_DIR_NAME:
            continue
        ok = generate_for_course(course_dir, force=force, logo=None, nome=None)
        gerados += 1 if ok else 0

        modo_dir = course_dir / scanner.OUTPUT_DIR_NAME
        index_html = modo_dir / "index.html"
        if index_html.exists():
            indexed.append((course_dir.name, modo_dir))

    print(f"\nConcluído: {gerados}/{len(candidates)} curso(s) processado(s).")

    if indexed:
        index_path = builder.generate_batch_index(parent_path, indexed)
        print(f"Índice de cursos: {index_path}")


HELP_EPILOG = """\
Exemplos:
  folderstream "D:\\Downloads\\Estudo\\Meu Curso"
  folderstream "D:\\Downloads\\Estudo" --batch
  folderstream "D:\\Downloads\\Estudo\\Meu Curso" --force
  folderstream "D:\\Downloads\\Estudo\\Meu Curso" --logo capa.png --nome "Meu Curso"
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="folderstream",
        description="Gera o FolderStream (player web local) para cursos locais.",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pasta", type=str, help="Pasta do curso (ou pasta-mãe, com --batch)")
    parser.add_argument("--batch", action="store_true", help="Trata 'pasta' como pasta-mãe contendo vários cursos")
    parser.add_argument("--force", action="store_true", help="Regenera mesmo se 'FolderStream' já existir")
    parser.add_argument("--logo", type=str, default=None, help="Caminho de uma imagem para usar como logo (ignorado em --batch)")
    parser.add_argument("--nome", type=str, default=None, help="Nome de exibição do curso (ignorado em --batch)")
    return parser


def main() -> int:
    # aceita "-help" (dash único) como sinônimo de "--help"/"-h", além do padrão do argparse
    argv = ["--help" if a == "-help" else a for a in sys.argv[1:]]

    parser = _build_parser()
    args = parser.parse_args(argv)

    root = Path(args.pasta)

    if args.batch:
        if args.logo or args.nome:
            print("[aviso] --logo e --nome são ignorados em modo --batch.")
        run_batch(root, force=args.force)
        return 0

    logo_path = Path(args.logo) if args.logo else None
    if logo_path and not logo_path.is_file():
        print(f"[erro] logo não encontrado: {logo_path}")
        return 1

    ok = generate_for_course(root, force=args.force, logo=logo_path, nome=args.nome)
    return 0 if ok else 1
