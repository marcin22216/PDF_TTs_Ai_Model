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


def test_run_job_builds_pdf_named_output_dir() -> None:
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
    outputs = run_job(request, runner=fake_runner, tts_factory=fake_tts_factory)

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

    request = JobRequest(pdf_path=pdf, output_base_dir=work / "out", model_path=model, use_cuda=True)
    run_job(request, runner=fake_runner, tts_factory=fake_tts_factory)

    assert captured["use_cuda"] is False


def test_run_job_falls_back_to_wav_when_ffmpeg_unavailable(monkeypatch) -> None:
    work = _work_dir()
    pdf = work / "Doc.pdf"
    model = work / "voice.onnx"
    pdf.write_bytes(b"%PDF-1.4")
    model.write_text("x", encoding="utf-8")
    captured = {}

    def fake_runner(*, config, tts_engine, progress_callback=None):
        captured["output_format"] = config.output_format
        return {"manifest": config.out_dir / "manifest.json", "merged_audio": config.out_dir / "full.wav"}

    def fake_tts_factory(**kwargs):
        return DummyTTS()

    monkeypatch.setattr(service, "ensure_onnxruntime_for_hardware", lambda auto_install=True: None)
    monkeypatch.setattr(service, "is_ffmpeg_available", lambda ffmpeg_exe="ffmpeg": False)

    request = JobRequest(
        pdf_path=pdf,
        output_base_dir=work / "out",
        model_path=model,
        output_format="mp3",
    )
    run_job(request, runner=fake_runner, tts_factory=fake_tts_factory)
    assert captured["output_format"] == "wav"


def test_run_job_passes_progress_callback() -> None:
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
    run_job(
        request,
        runner=fake_runner,
        tts_factory=fake_tts_factory,
        progress_callback=lambda p, s: events.append((p, s)),
    )

    assert captured["has_callback"] is True
    assert events == [(1, "init")]
