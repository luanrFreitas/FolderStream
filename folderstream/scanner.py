"""Varredura da pasta de um curso -> árvore de módulos/aulas/arquivos (manifest)."""
from __future__ import annotations

import json
import mimetypes
import re
import shutil
import struct
import subprocess
from pathlib import Path

from .manifest import make_file_id

OUTPUT_DIR_NAME = "FolderStream"

VIDEO_EXT = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv", ".m4v"}
SUBTITLE_EXT = {".vtt", ".srt"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
AUDIO_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
HTML_EXT = {".html", ".htm"}
PDF_EXT = {".pdf"}
ARCHIVE_EXT = {".zip", ".rar", ".7z"}

_NAT_SPLIT = re.compile(r"(\d+)")


def _natural_key(name: str):
    return [int(part) if part.isdigit() else part.lower() for part in _NAT_SPLIT.split(name)]


def _sorted_entries(folder: Path) -> list[Path]:
    return sorted(folder.iterdir(), key=lambda p: _natural_key(p.name))


def _kind_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in VIDEO_EXT:
        return "video"
    if ext in SUBTITLE_EXT:
        return "subtitle"
    if ext in HTML_EXT:
        return "html"
    if ext in PDF_EXT:
        return "pdf"
    if ext in IMAGE_EXT:
        return "image"
    if ext in AUDIO_EXT:
        return "audio"
    if ext in ARCHIVE_EXT:
        return "archive"
    return "other"


_FFPROBE_CACHE: dict[str, bool] = {}


def _ffprobe_available() -> bool:
    if "available" not in _FFPROBE_CACHE:
        _FFPROBE_CACHE["available"] = shutil.which("ffprobe") is not None
    return _FFPROBE_CACHE["available"]


def _get_video_duration_ffprobe(video_path: Path) -> float | None:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        duration = data.get("format", {}).get("duration")
        return round(float(duration), 3) if duration is not None else None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, OSError):
        return None


MP4_LIKE_EXT = {".mp4", ".mov", ".m4v"}


def _iter_boxes(f, start: int, end: int):
    """Itera boxes ISO-BMFF (MP4/MOV) em [start, end): (tipo, offset_do_payload, tamanho_do_payload)."""
    pos = start
    while pos < end:
        f.seek(pos)
        header = f.read(8)
        if len(header) < 8:
            return
        size, box_type = struct.unpack(">I4s", header)
        header_len = 8
        if size == 1:
            ext = f.read(8)
            if len(ext) < 8:
                return
            size = struct.unpack(">Q", ext)[0]
            header_len = 16
        elif size == 0:
            size = end - pos
        if size < header_len:
            return
        yield box_type, pos + header_len, size - header_len
        pos += size


def _find_box(f, target: bytes, start: int, end: int) -> tuple[int, int] | None:
    for box_type, payload_start, payload_size in _iter_boxes(f, start, end):
        if box_type == target:
            return payload_start, payload_size
    return None


def _read_mp4_duration(video_path: Path) -> float | None:
    """Lê a duração direto do box 'moov/mvhd' (MP4/MOV/M4V) sem depender de ffprobe.

    Cobre o formato usado por praticamente todo curso baixado (ISO-BMFF/QuickTime).
    Não tenta MKV/WebM/AVI (containers diferentes) — nesses casos o chamador deve
    cair para ffprobe ou aceitar duração ausente.
    """
    try:
        file_size = video_path.stat().st_size
        with open(video_path, "rb") as f:
            moov = _find_box(f, b"moov", 0, file_size)
            if moov is None:
                return None
            moov_start, moov_size = moov
            mvhd = _find_box(f, b"mvhd", moov_start, moov_start + moov_size)
            if mvhd is None:
                return None
            mvhd_start, mvhd_size = mvhd
            f.seek(mvhd_start)
            data = f.read(min(mvhd_size, 32))
            if len(data) < 4:
                return None
            version = data[0]
            if version == 1:
                if len(data) < 32:
                    return None
                timescale = struct.unpack(">I", data[20:24])[0]
                duration = struct.unpack(">Q", data[24:32])[0]
            else:
                if len(data) < 20:
                    return None
                timescale = struct.unpack(">I", data[12:16])[0]
                duration = struct.unpack(">I", data[16:20])[0]
            if not timescale:
                return None
            return round(duration / timescale, 3)
    except (OSError, struct.error, IndexError):
        return None


MKV_LIKE_EXT = {".mkv", ".webm"}

_EBML_ID_SEGMENT = 0x18538067
_EBML_ID_INFO = 0x1549A966
_EBML_ID_DURATION = 0x4489
_EBML_ID_TIMECODE_SCALE = 0x2AD7B1
_EBML_DEFAULT_TIMECODE_SCALE = 1_000_000 


def _read_vint(f, *, keep_marker: bool) -> tuple[int, int] | None:
    """Lê um VINT (EBML variable-length integer) na posição atual de f.

    Retorna (valor, bytes_consumidos) ou None em EOF/dado inválido. Element IDs
    mantêm o bit de marcação de tamanho no valor (keep_marker=True); tamanhos de
    elemento têm o bit de marcação removido (keep_marker=False), conforme a spec.
    """
    first = f.read(1)
    if not first:
        return None
    b0 = first[0]
    if b0 == 0:
        return None
    length = 1
    mask = 0x80
    while not (b0 & mask):
        mask >>= 1
        length += 1
        if length > 8:
            return None
    rest = f.read(length - 1)
    if len(rest) < length - 1:
        return None
    value = b0 if keep_marker else (b0 & (mask - 1))
    for byte in rest:
        value = (value << 8) | byte
    return value, length


def _iter_ebml(f, start: int, end: int):
    """Itera elementos EBML top-level em [start, end): (id, offset_payload, fim_payload)."""
    pos = start
    while pos < end:
        f.seek(pos)
        id_result = _read_vint(f, keep_marker=True)
        if id_result is None:
            return
        elem_id, _ = id_result
        size_result = _read_vint(f, keep_marker=False)
        if size_result is None:
            return
        size_val, size_len = size_result
        payload_start = f.tell()
        unknown_size = size_val == (1 << (7 * size_len)) - 1
        payload_end = end if unknown_size else payload_start + size_val
        if payload_end < payload_start or payload_end > end:
            payload_end = end
        yield elem_id, payload_start, payload_end
        pos = payload_end


def _read_ebml_uint(f, start: int, end: int) -> int | None:
    size = end - start
    if size <= 0 or size > 8:
        return None
    f.seek(start)
    data = f.read(size)
    if len(data) < size:
        return None
    value = 0
    for byte in data:
        value = (value << 8) | byte
    return value


def _read_ebml_float(f, start: int, end: int) -> float | None:
    size = end - start
    f.seek(start)
    data = f.read(size)
    if size == 4 and len(data) == 4:
        return struct.unpack(">f", data)[0]
    if size == 8 and len(data) == 8:
        return struct.unpack(">d", data)[0]
    return None


def _read_mkv_duration(video_path: Path) -> float | None:
    """Lê a duração do elemento Segment/Info/Duration (Matroska/WebM), sem ffprobe.

    Cobre arquivos bem formados por qualquer encoder padrão. Se o Duration não
    estiver presente (streams ao vivo não finalizados, raro em cursos baixados),
    retorna None — o chamador pode cair para ffprobe se disponível.
    """
    try:
        file_size = video_path.stat().st_size
        with open(video_path, "rb") as f:
            segment = None
            for elem_id, payload_start, payload_end in _iter_ebml(f, 0, file_size):
                if elem_id == _EBML_ID_SEGMENT:
                    segment = (payload_start, payload_end)
                    break
            if segment is None:
                return None
            seg_start, seg_end = segment

            info = None
            for elem_id, payload_start, payload_end in _iter_ebml(f, seg_start, seg_end):
                if elem_id == _EBML_ID_INFO:
                    info = (payload_start, payload_end)
                    break
            if info is None:
                return None
            info_start, info_end = info

            timecode_scale = _EBML_DEFAULT_TIMECODE_SCALE
            duration_raw = None
            for elem_id, payload_start, payload_end in _iter_ebml(f, info_start, info_end):
                if elem_id == _EBML_ID_TIMECODE_SCALE:
                    value = _read_ebml_uint(f, payload_start, payload_end)
                    if value:
                        timecode_scale = value
                elif elem_id == _EBML_ID_DURATION:
                    duration_raw = _read_ebml_float(f, payload_start, payload_end)

            if duration_raw is None:
                return None
            return round(duration_raw * timecode_scale / 1_000_000_000, 3)
    except (OSError, struct.error, IndexError):
        return None


def _iter_riff(f, start: int, end: int):
    """Itera chunks RIFF (AVI) em [start, end): (fourcc, offset_payload, tamanho_payload)."""
    pos = start
    while pos + 8 <= end:
        f.seek(pos)
        header = f.read(8)
        if len(header) < 8:
            return
        fourcc = header[0:4]
        size = struct.unpack("<I", header[4:8])[0]
        payload_start = pos + 8
        yield fourcc, payload_start, size
        pos = payload_start + size + (size & 1)  # chunks são alinhados a 2 bytes


def _read_avi_duration(video_path: Path) -> float | None:
    """Lê a duração do chunk 'avih' (AVI Main Header) dentro de LIST 'hdrl', sem ffprobe."""
    try:
        file_size = video_path.stat().st_size
        with open(video_path, "rb") as f:
            header = f.read(12)
            if len(header) < 12 or header[0:4] != b"RIFF" or header[8:12] != b"AVI ":
                return None
            for fourcc, payload_start, size in _iter_riff(f, 12, file_size):
                if fourcc != b"LIST":
                    continue
                f.seek(payload_start)
                list_type = f.read(4)
                if list_type != b"hdrl":
                    continue
                for sub_fourcc, sub_start, sub_size in _iter_riff(f, payload_start + 4, payload_start + size):
                    if sub_fourcc == b"avih":
                        f.seek(sub_start)
                        data = f.read(min(sub_size, 20))
                        if len(data) < 20:
                            return None
                        micro_sec_per_frame = struct.unpack("<I", data[0:4])[0]
                        total_frames = struct.unpack("<I", data[16:20])[0]
                        if not micro_sec_per_frame:
                            return None
                        return round(micro_sec_per_frame * total_frames / 1_000_000, 3)
                return None  # achou hdrl mas não achou avih -> arquivo malformado
        return None
    except (OSError, struct.error, IndexError):
        return None


def get_video_duration(video_path: Path) -> float | None:
    """Duração em segundos. Usa ffprobe se disponível (qualquer formato); senão,
    tenta um parser dependência-zero por formato de container:
    - MP4/MOV/M4V (ISO-BMFF): box moov/mvhd
    - MKV/WebM (Matroska/EBML): Segment/Info/Duration
    - AVI (RIFF): chunk avih dentro de LIST hdrl
    FLV e WMV/ASF ainda dependem de ffprobe (raros em cursos baixados hoje)."""
    if _ffprobe_available():
        duration = _get_video_duration_ffprobe(video_path)
        if duration is not None:
            return duration
    ext = video_path.suffix.lower()
    if ext in MP4_LIKE_EXT:
        return _read_mp4_duration(video_path)
    if ext in MKV_LIKE_EXT:
        return _read_mkv_duration(video_path)
    if ext == ".avi":
        return _read_avi_duration(video_path)
    return None


DURATION_CACHE_FILENAME = ".duration_cache.json"


def load_duration_cache(modo_plataforma_dir: Path) -> dict:
    """Cache de duração por arquivo (chave = path relativo), para não rodar ffprobe de novo
    em vídeos que não mudaram entre gerações (RNF05)."""
    cache_file = modo_plataforma_dir / DURATION_CACHE_FILENAME
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def write_duration_cache(modo_plataforma_dir: Path, cache: dict) -> None:
    (modo_plataforma_dir / DURATION_CACHE_FILENAME).write_text(
        json.dumps(cache, ensure_ascii=False), encoding="utf-8"
    )


def scan_course(course_root: Path, *, compute_duration: bool = True) -> tuple[list[dict], Path, dict]:
    """Varre a pasta do curso e devolve (modules, modo_plataforma_dir, duration_cache)."""
    course_root = course_root.resolve()
    modo_plataforma_dir = course_root / OUTPUT_DIR_NAME
    old_cache = load_duration_cache(modo_plataforma_dir)
    new_cache: dict = {}

    def rel_path(p: Path) -> str:
        rel = p.relative_to(course_root).as_posix()
        return f"../{rel}"

    def resolve_duration(file_path: Path, rel_key: str) -> float | None:
        if not compute_duration:
            return None
        stat = file_path.stat()
        fingerprint = {"size": stat.st_size, "mtime": stat.st_mtime}
        cached = old_cache.get(rel_key)
        if cached and cached.get("size") == fingerprint["size"] and cached.get("mtime") == fingerprint["mtime"]:
            duration = cached.get("duration")
        else:
            duration = get_video_duration(file_path)
        new_cache[rel_key] = {**fingerprint, "duration": duration}
        return duration

    def build_file_entry(file_path: Path, siblings: list[Path]) -> dict:
        kind = _kind_for(file_path)
        rel = rel_path(file_path)
        entry = {
            "id": make_file_id(rel),
            "name": file_path.name,
            "path": rel,
            "mime": mimetypes.guess_type(file_path.name)[0] or "application/octet-stream",
            "kind": kind,
        }
        if kind == "video":
            entry["duration"] = resolve_duration(file_path, rel)
            base = file_path.stem.lower()
            subs = []
            for sib in siblings:
                if sib.suffix.lower() in SUBTITLE_EXT and sib.stem.lower().startswith(base) and sib != file_path:
                    suffix = sib.stem[len(file_path.stem):].strip(".-_ ").lower()
                    lang = suffix if suffix else "pt-br"
                    subs.append({"path": rel_path(sib), "lang": lang, "label": lang.upper()})
            entry["subtitles"] = subs
        return entry

    def walk_lesson(folder: Path) -> dict:
        entries = _sorted_entries(folder)
        sub_dirs = [e for e in entries if e.is_dir()]
        sub_files = [e for e in entries if e.is_file() and e.suffix.lower() not in SUBTITLE_EXT]
        all_files_in_folder = [e for e in entries if e.is_file()]

        files = [build_file_entry(f, all_files_in_folder) for f in sub_files]
        lessons = [walk_lesson(d) for d in sub_dirs]

        video_pairs = [(p, e) for p, e in zip(sub_files, files) if e["kind"] == "video"]
        if len(video_pairs) > 1:
            # Vários vídeos soltos direto na mesma pasta (em vez de 1 vídeo por
            # subpasta) — sem isso, o player só mostraria o 1º como "aula" e
            # esconderia o resto. Cada vídeo vira sua própria aula sintética,
            # nomeada pelo próprio arquivo; materiais não-vídeo da pasta (ex.:
            # um descricao.html compartilhado) ficam anexados a cada uma.
            non_video_files = [e for e in files if e["kind"] != "video"]
            synthetic_lessons = [
                {"name": p.stem, "files": [e] + non_video_files, "lessons": []}
                for p, e in video_pairs
            ]
            return {"name": folder.name, "files": [], "lessons": synthetic_lessons + lessons}

        return {"name": folder.name, "files": files, "lessons": lessons}

    modules = []
    for entry in _sorted_entries(course_root):
        if not entry.is_dir():
            continue
        if entry.name == OUTPUT_DIR_NAME:
            continue
        if entry.name.startswith("."):
            continue
        lesson_node = walk_lesson(entry)
        modules.append({"name": lesson_node["name"], "lessons": lesson_node["lessons"] or _files_only_as_lesson(lesson_node)})

    return modules, modo_plataforma_dir, new_cache


def _files_only_as_lesson(node: dict) -> list[dict]:
    """Se o módulo tiver arquivos soltos direto na raiz (sem subpasta de aula), vira 1 aula única."""
    if node["files"]:
        return [{"name": node["name"], "files": node["files"], "lessons": []}]
    return []
