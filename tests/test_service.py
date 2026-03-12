from pathlib import Path
from uuid import uuid4

import pytest

import pdf_tts_ai.service as service
from pdf_tts_ai.service import JobRequest, run_job, validate_request


def _work_dir() -> Path:
    base = Path.cwd() / "tests_runtime"
    base.mkdir(parents=True, exist_ok=True)
    work = base / uuid4().hex
    work.mkdir(parents=True, exist_ok=False)
    return work


class DummyTTS:
    pass


def test_validate_request_rejects_non_pdf_file() -> None:
    work = _work_dir()
    input_file = work / "input.txt"
    model = work / "voice.onnx"
    input_file.write_text("x", encoding="utf-8")
    model.write_text("x", encoding="utf-8")

    request = JobRequest(pdf_path=input_file, output_base_dir=work, model_path=model)
    with pytest.raises(ValueError):
        validate_request(request)


def test_validate_request_rejects_invalid_output_format() -> None:
    work = _work_dir()
    pdf = work / "input.pdf"
    model = work / "voice.onnx"
    pdf.write_bytes(b"%PDF-1.4")
    model.write_text("x", encoding="utf-8")
    request = JobRequest(
        pdf_path=pdf,
        output_base_dir=work,
        model_path=model,
        output_format="flac",
    )
    with pytest.raises(ValueError):
        validate_request(request)


def test_run_job_builds_pdf_named_output_dir(monkeypatch) -> None:
    work = _work_dir()
    pdf = work / "Dokument testowy.pdf"
    model = work / "voice.onnx"
    pdf.write_bytes(b"%PDF-1.4")
    model.write_text("dummy", encoding="utf-8")

    captured = {}

    def fake_runner(*, config, tts_engine):
        captured["out_dir"] = config.out_dir
        captured["pdf_path"] = config.pdf_path
        captured["output_format"] = config.output_format
        captured["tts_engine_type"] = type(tts_engine).__name__
        return {"manifest": config.out_dir / "manifest.json", "merged_audio": config.out_dir / "full.wav"}

    def fake_tts_factory(**kwargs):
        captured["tts_kwargs"] = kwargs
        return DummyTTS()

    request = JobRequest(
        pdf_path=pdf,
        output_base_dir=work / "out_base",
        model_path=model,
        piper_exe="C:\\tools\\piper.exe",
    )
    monkeypatch.setattr(service, "ensure_onnxruntime_for_hardware", lambda auto_install=True: None)
    monkeypatch.setattr(service, "resolve_selected_pages", lambda request: [1, 2])

    outputs = run_job(
        request,
        runner=fake_runner,
        tts_factory=fake_tts_factory,
    )

    assert captured["out_dir"].name == "Dokument_testowy"
    assert captured["pdf_path"] == pdf
    assert captured["output_format"] == "wav"
    assert captured["tts_engine_type"] == "DummyTTS"
    assert captured["tts_kwargs"]["piper_exe"] == "C:\\tools\\piper.exe"
    assert captured["tts_kwargs"]["use_cuda"] is False
    assert outputs["merged_audio"].name == "full.wav"


def test_run_job_falls_back_to_cpu_when_cuda_unavailable(monkeypatch) -> None:
    work = _work_dir()
    pdf = work / "Dokument.pdf"
    model = work / "voice.onnx"
    pdf.write_bytes(b"%PDF-1.4")
    model.write_text("x", encoding="utf-8")
    captured = {}

    def fake_runner(*, config, tts_engine, progress_callback=None):
        return {"manifest": config.out_dir / "manifest.json", "merged_audio": config.out_dir / "full.wav"}

    def fake_tts_factory(**kwargs):
        captured["use_cuda"] = kwargs["use_cuda"]
        return DummyTTS()

    monkeypatch.setattr(service, "ensure_onnxruntime_for_hardware", lambda auto_install=True: None)
    monkeypatch.setattr(service, "has_nvidia_gpu", lambda: True)
    monkeypatch.setattr(service, "is_cuda_provider_available", lambda: False)
    monkeypatch.setattr(service, "resolve_selected_pages", lambda request: [1])

    request = JobRequest(pdf_path=pdf, output_base_dir=work / "out", model_path=model, use_cuda=True)
    run_job(request, runner=fake_runner, tts_factory=fake_tts_factory)

    assert captured["use_cuda"] is False


def test_run_job_raises_when_ffmpeg_unavailable_for_compressed_formats(monkeypatch) -> None:
    work = _work_dir()
    pdf = work / "Doc.pdf"
    model = work / "voice.onnx"
    pdf.write_bytes(b"%PDF-1.4")
    model.write_text("x", encoding="utf-8")

    def fake_tts_factory(**kwargs):
        return DummyTTS()

    monkeypatch.setattr(service, "ensure_onnxruntime_for_hardware", lambda auto_install=True: None)
    monkeypatch.setattr(service, "is_ffmpeg_available", lambda ffmpeg_exe="ffmpeg": False)
    monkeypatch.setattr(service, "resolve_selected_pages", lambda request: [1])

    request = JobRequest(
        pdf_path=pdf,
        output_base_dir=work / "out",
        model_path=model,
        output_format="mp3",
    )
    with pytest.raises(RuntimeError, match="requires ffmpeg"):
        run_job(request, runner=lambda **kwargs: {}, tts_factory=fake_tts_factory)


def test_run_job_passes_progress_callback(monkeypatch) -> None:
    work = _work_dir()
    pdf = work / "Dokument.pdf"
    model = work / "voice.onnx"
    pdf.write_bytes(b"%PDF-1.4")
    model.write_text("dummy", encoding="utf-8")

    captured = {"has_callback": False}

    def fake_runner(*, config, tts_engine, progress_callback=None):
        captured["has_callback"] = callable(progress_callback)
        if progress_callback:
            progress_callback(1, "init")
        return {"manifest": config.out_dir / "manifest.json", "merged_audio": config.out_dir / "full.wav"}

    def fake_tts_factory(**kwargs):
        return DummyTTS()

    events: list[tuple[int, str]] = []
    request = JobRequest(pdf_path=pdf, output_base_dir=work / "out_base", model_path=model)
    monkeypatch.setattr(service, "ensure_onnxruntime_for_hardware", lambda auto_install=True: None)
    monkeypatch.setattr(service, "resolve_selected_pages", lambda request: [1])

    run_job(
        request,
        runner=fake_runner,
        tts_factory=fake_tts_factory,
        progress_callback=lambda p, s: events.append((p, s)),
    )

    assert captured["has_callback"] is True
    assert events == [(1, "init")]


def test_resolve_selected_pages_from_page_range(monkeypatch) -> None:
    request = JobRequest(
        pdf_path=Path("dummy.pdf"),
        output_base_dir=Path("."),
        model_path=Path("m.onnx"),
        page_range="2-4,6",
    )
    monkeypatch.setattr(service, "get_page_count", lambda path: 8)
    monkeypatch.setattr(service, "extract_toc", lambda path: [])
    pages = service.resolve_selected_pages(request)
    assert pages == [2, 3, 4, 6]


def test_resolve_selected_pages_with_toc_selection(monkeypatch) -> None:
    request = JobRequest(
        pdf_path=Path("dummy.pdf"),
        output_base_dir=Path("."),
        model_path=Path("m.onnx"),
        page_range="",
        chapter_range="2-3",
    )
    monkeypatch.setattr(service, "get_page_count", lambda path: 10)
    monkeypatch.setattr(
        service,
        "extract_toc",
        lambda path: [
            service.TocEntry(index=1, level=1, title="A", page=1),
            service.TocEntry(index=2, level=1, title="B", page=4),
            service.TocEntry(index=3, level=1, title="C", page=7),
        ],
    )
    pages = service.resolve_selected_pages(request)
    assert pages == [4, 5, 6, 7, 8, 9, 10]


def test_resolve_selected_pages_intersects_page_and_toc(monkeypatch) -> None:
    request = JobRequest(
        pdf_path=Path("dummy.pdf"),
        output_base_dir=Path("."),
        model_path=Path("m.onnx"),
        page_range="5-8",
        chapter_range="2",
    )
    monkeypatch.setattr(service, "get_page_count", lambda path: 10)
    monkeypatch.setattr(
        service,
        "extract_toc",
        lambda path: [
            service.TocEntry(index=1, level=1, title="A", page=1),
            service.TocEntry(index=2, level=1, title="B", page=4),
            service.TocEntry(index=3, level=1, title="C", page=7),
        ],
    )
    pages = service.resolve_selected_pages(request)
    assert pages == [5, 6]


def test_resolve_selected_pages_raises_for_chapters_without_toc(monkeypatch) -> None:
    request = JobRequest(
        pdf_path=Path("dummy.pdf"),
        output_base_dir=Path("."),
        model_path=Path("m.onnx"),
        chapter_range="1",
    )
    monkeypatch.setattr(service, "get_page_count", lambda path: 5)
    monkeypatch.setattr(service, "extract_toc", lambda path: [])
    with pytest.raises(ValueError):
        service.resolve_selected_pages(request)
