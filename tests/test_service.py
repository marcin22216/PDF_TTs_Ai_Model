from pathlib import Path
from uuid import uuid4

import pytest

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
        captured["tts_engine_type"] = type(tts_engine).__name__
        return {"manifest": config.out_dir / "manifest.json", "merged_audio": config.out_dir / "full.wav"}

    def fake_tts_factory(**kwargs):
        captured["tts_kwargs"] = kwargs
        return DummyTTS()

    request = JobRequest(pdf_path=pdf, output_base_dir=work / "out_base", model_path=model)
    outputs = run_job(request, runner=fake_runner, tts_factory=fake_tts_factory)

    assert captured["out_dir"].name == "Dokument_testowy"
    assert captured["pdf_path"] == pdf
    assert captured["tts_engine_type"] == "DummyTTS"
    assert outputs["merged_audio"].name == "full.wav"
