from pathlib import Path
import subprocess
from uuid import uuid4

import pytest

from pdf_tts_ai.tts import PiperTTS, _clean_text_for_tts


def _work_dir() -> Path:
    base = Path.cwd() / "tests_runtime"
    base.mkdir(parents=True, exist_ok=True)
    work = base / uuid4().hex
    work.mkdir(parents=True, exist_ok=False)
    return work


def test_clean_text_for_tts_removes_unsupported_chars() -> None:
    text = "Ala ma kota ☺ — test € oraz é i ą."
    cleaned = _clean_text_for_tts(text)
    assert "☺" not in cleaned
    assert "€" not in cleaned
    assert "Ala ma kota" in cleaned
    assert "ą" in cleaned


def test_synthesize_to_wav_raises_readable_error(monkeypatch) -> None:
    work_dir = _work_dir()

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["piper"],
            stderr=b"mock error from piper",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    tts = PiperTTS(model_path=work_dir / "voice.onnx", piper_exe="piper")

    with pytest.raises(RuntimeError) as exc:
        tts.synthesize_to_wav("Przykladowy tekst", work_dir / "out.wav")

    assert "mock error from piper" in str(exc.value)


def test_synthesize_uses_input_file_and_cuda_flag(monkeypatch) -> None:
    work_dir = _work_dir()
    captured = {"cmd": None, "kwargs": None}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return None

    monkeypatch.setattr(subprocess, "run", fake_run)
    tts = PiperTTS(model_path=work_dir / "voice.onnx", piper_exe="piper", use_cuda=True)
    tts.synthesize_to_wav("Przykladowy tekst", work_dir / "out.wav")

    assert "--cuda" in captured["cmd"]
    assert "--input_file" in captured["cmd"]
    assert "input" not in captured["kwargs"]
