import struct
from pathlib import Path

import pytest

from folderstream import scanner


def touch(path: Path, content: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def no_real_ffprobe(monkeypatch):
    """Testes não devem depender de ffprobe estar instalado nem invocá-lo de verdade.

    Força o dispatcher a sempre "achar" ffprobe e stuba só a chamada ao binário
    (não o get_video_duration inteiro), para que:
    - o resultado seja o mesmo (42.0) rodando com ou sem ffprobe real instalado
      na máquina que roda os testes;
    - o fallback MP4 puro-Python continue testável de verdade em testes que
      sobrescrevem _ffprobe_available para False.
    """
    monkeypatch.setattr(scanner, "_ffprobe_available", lambda: True)
    monkeypatch.setattr(scanner, "_get_video_duration_ffprobe", lambda path: 42.0)


def test_natural_sort_order(tmp_path):
    touch(tmp_path / "1. Intro" / "Aula.mp4")
    touch(tmp_path / "2. Meio" / "Aula.mp4")
    touch(tmp_path / "10. Fim" / "Aula.mp4")

    modules, _, _ = scanner.scan_course(tmp_path)

    assert [m["name"] for m in modules] == ["1. Intro", "2. Meio", "10. Fim"]


def test_kind_detection_and_subtitle_association(tmp_path):
    lesson_dir = tmp_path / "001. Mod" / "001. Aula"
    touch(lesson_dir / "Aula.mp4")
    touch(lesson_dir / "Aula.pt-br.srt")
    touch(lesson_dir / "descricao.html", "<p>oi</p>")

    modules, _, _ = scanner.scan_course(tmp_path)
    files = modules[0]["lessons"][0]["files"]
    by_name = {f["name"]: f for f in files}

    assert by_name["Aula.mp4"]["kind"] == "video"
    assert by_name["Aula.mp4"]["duration"] == 42.0
    assert by_name["descricao.html"]["kind"] == "html"
    assert "duration" not in by_name["descricao.html"]

    subs = by_name["Aula.mp4"]["subtitles"]
    assert len(subs) == 1
    assert subs[0]["lang"] == "pt-br"
    assert subs[0]["path"].endswith("Aula.pt-br.srt")

    assert "Aula.pt-br.srt" not in by_name


def test_loose_files_become_synthetic_lesson(tmp_path):
    touch(tmp_path / "003. Modulo Solto" / "Aula.mp4")

    modules, _, _ = scanner.scan_course(tmp_path)

    assert len(modules) == 1
    assert modules[0]["name"] == "003. Modulo Solto"
    assert len(modules[0]["lessons"]) == 1
    assert modules[0]["lessons"][0]["name"] == "003. Modulo Solto"
    assert modules[0]["lessons"][0]["files"][0]["name"] == "Aula.mp4"


def test_multiple_videos_in_same_folder_become_separate_lessons(tmp_path):
    lesson_dir = tmp_path / "01 - Ter ideias"
    touch(lesson_dir / "01 - Introducao.mp4")
    touch(lesson_dir / "02 - Ter ideias.mp4")
    touch(lesson_dir / "03 - Brainstorm.mp4")

    modules, _, _ = scanner.scan_course(tmp_path)
    lessons = modules[0]["lessons"]

    assert len(lessons) == 3
    assert [l["name"] for l in lessons] == ["01 - Introducao", "02 - Ter ideias", "03 - Brainstorm"]
    for lesson in lessons:
        assert len(lesson["files"]) == 1
        assert lesson["files"][0]["kind"] == "video"


def test_multiple_videos_nested_two_levels_deep(tmp_path):
    lesson_dir = tmp_path / "001. Modulo 4" / "01 - Ter ideias"
    touch(lesson_dir / "01 - Introducao.mp4")
    touch(lesson_dir / "02 - Ter ideias.mp4")
    touch(lesson_dir / "03 - Brainstorm.mp4")

    modules, _, _ = scanner.scan_course(tmp_path)
    group = modules[0]["lessons"][0]

    assert group["name"] == "01 - Ter ideias"
    assert group["files"] == []
    assert len(group["lessons"]) == 3
    assert [l["name"] for l in group["lessons"]] == ["01 - Introducao", "02 - Ter ideias", "03 - Brainstorm"]


def test_multiple_videos_share_common_attachment(tmp_path):
    lesson_dir = tmp_path / "01 - Aulas"
    touch(lesson_dir / "01 - A.mp4")
    touch(lesson_dir / "02 - B.mp4")
    touch(lesson_dir / "descricao.html", "<p>material comum às duas aulas</p>")

    modules, _, _ = scanner.scan_course(tmp_path)
    lessons = modules[0]["lessons"]

    assert len(lessons) == 2
    for lesson in lessons:
        kinds = sorted(f["kind"] for f in lesson["files"])
        assert kinds == ["html", "video"]
        assert any(f["name"] == "descricao.html" for f in lesson["files"])


def test_single_video_in_folder_stays_as_one_lesson(tmp_path):
    lesson_dir = tmp_path / "001. Mod" / "001. Aula"
    touch(lesson_dir / "Aula.mp4")
    touch(lesson_dir / "descricao.html")

    modules, _, _ = scanner.scan_course(tmp_path)
    lessons = modules[0]["lessons"]

    assert len(lessons) == 1
    assert lessons[0]["name"] == "001. Aula"
    assert len(lessons[0]["files"]) == 2


def test_nested_sub_lessons(tmp_path):
    touch(tmp_path / "001. Mod" / "001. Aula" / "001. Parte A" / "Aula.mp4")

    modules, _, _ = scanner.scan_course(tmp_path)
    lesson = modules[0]["lessons"][0]
    assert lesson["name"] == "001. Aula"
    assert lesson["files"] == []
    assert len(lesson["lessons"]) == 1
    assert lesson["lessons"][0]["name"] == "001. Parte A"
    assert lesson["lessons"][0]["files"][0]["name"] == "Aula.mp4"


def test_output_folder_and_hidden_folders_are_skipped(tmp_path):
    touch(tmp_path / "001. Mod" / "001. Aula" / "Aula.mp4")
    touch(tmp_path / scanner.OUTPUT_DIR_NAME / "index.html", "<html></html>")
    touch(tmp_path / ".git" / "config", "")

    modules, modo_plataforma_dir, _ = scanner.scan_course(tmp_path)

    assert [m["name"] for m in modules] == ["001. Mod"]
    assert modo_plataforma_dir == (tmp_path / scanner.OUTPUT_DIR_NAME).resolve()


def test_duration_cache_avoids_recomputing_unchanged_video(tmp_path, monkeypatch):
    video = touch(tmp_path / "001. Mod" / "001. Aula" / "Aula.mp4")

    calls = []

    def fake_ffprobe(path):
        calls.append(path)
        return 10.0

    monkeypatch.setattr(scanner, "get_video_duration", fake_ffprobe)

    modules1, modo_dir, cache1 = scanner.scan_course(tmp_path)
    assert modules1[0]["lessons"][0]["files"][0]["duration"] == 10.0
    assert len(calls) == 1

    modo_dir.mkdir(parents=True, exist_ok=True)
    scanner.write_duration_cache(modo_dir, cache1)

    modules2, _, cache2 = scanner.scan_course(tmp_path)
    assert modules2[0]["lessons"][0]["files"][0]["duration"] == 10.0
    assert len(calls) == 1  # continua 1, não 2

    video.write_text("conteudo maior agora", encoding="utf-8")
    scanner.scan_course(tmp_path)
    assert len(calls) == 2


def test_compute_duration_false_skips_ffprobe_entirely(tmp_path, monkeypatch):
    touch(tmp_path / "001. Mod" / "001. Aula" / "Aula.mp4")
    calls = []
    monkeypatch.setattr(scanner, "get_video_duration", lambda path: calls.append(path) or 1.0)

    modules, _, _ = scanner.scan_course(tmp_path, compute_duration=False)

    assert modules[0]["lessons"][0]["files"][0]["duration"] is None
    assert calls == []


def _make_box(box_type: bytes, payload: bytes) -> bytes:
    import struct
    return struct.pack(">I4s", 8 + len(payload), box_type) + payload


def _make_minimal_mp4(seconds: float, timescale: int = 1000) -> bytes:
    import struct
    duration_units = round(seconds * timescale)
    mvhd_payload = (
        struct.pack(">I", 0)              # version(1) + flags(3)
        + struct.pack(">I", 0)            # creation_time
        + struct.pack(">I", 0)            # modification_time
        + struct.pack(">I", timescale)    # timescale
        + struct.pack(">I", duration_units)  # duration
    )
    ftyp = _make_box(b"ftyp", b"isom" + struct.pack(">I", 512) + b"isomiso2avc1mp41")
    moov = _make_box(b"moov", _make_box(b"mvhd", mvhd_payload))
    return ftyp + moov


def test_read_mp4_duration_parses_mvhd_box(tmp_path):
    video = tmp_path / "Aula.mp4"
    video.write_bytes(_make_minimal_mp4(125.0))

    assert scanner._read_mp4_duration(video) == 125.0


def test_read_mp4_duration_version1_64bit(tmp_path):
    import struct
    timescale = 1000
    duration_units = 90_000  
    mvhd_payload = (
        struct.pack(">I", 1 << 24)         # version=1 (top byte) + flags=0
        + struct.pack(">Q", 0)             # creation_time (64-bit)
        + struct.pack(">Q", 0)             # modification_time (64-bit)
        + struct.pack(">I", timescale)
        + struct.pack(">Q", duration_units)
    )
    data = _make_box(b"ftyp", b"isom") + _make_box(b"moov", _make_box(b"mvhd", mvhd_payload))
    video = tmp_path / "Aula.mov"
    video.write_bytes(data)

    assert scanner._read_mp4_duration(video) == 90.0


def test_read_mp4_duration_missing_moov_returns_none(tmp_path):
    video = tmp_path / "Aula.mp4"
    video.write_bytes(_make_box(b"ftyp", b"isom"))  # sem moov/mvhd

    assert scanner._read_mp4_duration(video) is None


def test_get_video_duration_falls_back_to_mp4_parser_without_ffprobe(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner, "_ffprobe_available", lambda: False)
    video = tmp_path / "Aula.mp4"
    video.write_bytes(_make_minimal_mp4(42.5))

    assert scanner.get_video_duration(video) == 42.5


def test_get_video_duration_without_ffprobe_and_unsupported_container_is_none(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner, "_ffprobe_available", lambda: False)
    video = tmp_path / "Aula.wmv"  # WMV/ASF não tem parser puro-Python (ainda)
    video.write_bytes(b"not a real wmv file")

    assert scanner.get_video_duration(video) is None


def _ebml_size_vint(value: int) -> bytes:
    length = 1
    while value > (1 << (7 * length)) - 2:
        length += 1
    marker = 1 << (7 * length)
    return (marker | value).to_bytes(length, "big")


def _ebml_elem(id_int: int, id_bytelen: int, payload: bytes) -> bytes:
    return id_int.to_bytes(id_bytelen, "big") + _ebml_size_vint(len(payload)) + payload


def _make_minimal_mkv(duration_value: float, timecode_scale: int) -> bytes:
    duration_elem = _ebml_elem(0x4489, 2, struct.pack(">d", duration_value))
    scale_elem = _ebml_elem(0x2AD7B1, 3, timecode_scale.to_bytes(4, "big"))
    info_elem = _ebml_elem(0x1549A966, 4, scale_elem + duration_elem)
    segment_elem = _ebml_elem(0x18538067, 4, info_elem)
    ebml_header = _ebml_elem(0x1A45DFA3, 4, b"")
    return ebml_header + segment_elem


def test_read_mkv_duration_parses_segment_info(tmp_path):
    video = tmp_path / "Aula.mkv"
    video.write_bytes(_make_minimal_mkv(duration_value=45000.0, timecode_scale=2_000_000))

    assert scanner._read_mkv_duration(video) == 90.0


def test_read_mkv_duration_webm_extension_also_supported(tmp_path):
    video = tmp_path / "Aula.webm"
    video.write_bytes(_make_minimal_mkv(duration_value=125000.0, timecode_scale=1_000_000))

    assert scanner._read_mkv_duration(video) == 125.0


def test_read_mkv_duration_missing_segment_returns_none(tmp_path):
    video = tmp_path / "Aula.mkv"
    video.write_bytes(_ebml_elem(0x1A45DFA3, 4, b""))  # só o header, sem Segment

    assert scanner._read_mkv_duration(video) is None


def test_get_video_duration_falls_back_to_mkv_parser_without_ffprobe(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner, "_ffprobe_available", lambda: False)
    video = tmp_path / "Aula.webm"
    video.write_bytes(_make_minimal_mkv(duration_value=10000.0, timecode_scale=1_000_000))

    assert scanner.get_video_duration(video) == 10.0


def _make_minimal_avi(micro_sec_per_frame: int, total_frames: int) -> bytes:
    avih_payload = struct.pack("<IIIII", micro_sec_per_frame, 0, 0, 0, total_frames)
    avih_chunk = b"avih" + struct.pack("<I", len(avih_payload)) + avih_payload
    hdrl_payload = b"hdrl" + avih_chunk
    list_chunk = b"LIST" + struct.pack("<I", len(hdrl_payload)) + hdrl_payload
    riff_body = b"AVI " + list_chunk
    return b"RIFF" + struct.pack("<I", len(riff_body)) + riff_body


def test_read_avi_duration_parses_avih_chunk(tmp_path):
    video = tmp_path / "Aula.avi"
    video.write_bytes(_make_minimal_avi(micro_sec_per_frame=40_000, total_frames=3000))

    # 40_000us/frame * 3000 frames = 120_000_000us = 120.0s
    assert scanner._read_avi_duration(video) == 120.0


def test_read_avi_duration_missing_avih_returns_none(tmp_path):
    hdrl_payload = b"hdrl"  # sem avih dentro
    list_chunk = b"LIST" + struct.pack("<I", len(hdrl_payload)) + hdrl_payload
    riff_body = b"AVI " + list_chunk
    data = b"RIFF" + struct.pack("<I", len(riff_body)) + riff_body
    video = tmp_path / "Aula.avi"
    video.write_bytes(data)

    assert scanner._read_avi_duration(video) is None


def test_read_avi_duration_not_a_riff_file_returns_none(tmp_path):
    video = tmp_path / "Aula.avi"
    video.write_bytes(b"not a real avi file")

    assert scanner._read_avi_duration(video) is None


def test_get_video_duration_falls_back_to_avi_parser_without_ffprobe(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner, "_ffprobe_available", lambda: False)
    video = tmp_path / "Aula.avi"
    video.write_bytes(_make_minimal_avi(micro_sec_per_frame=20_000, total_frames=1500))

    assert scanner.get_video_duration(video) == 30.0
