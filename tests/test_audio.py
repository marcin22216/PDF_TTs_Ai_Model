from pathlib import Path
from uuid import uuid4
import wave

import pytest

from pdf_tts_ai.audio import merge_wav_files


def _write_wav(path: Path, framerate: int = 22050, duration_frames: int = 2205) -> None:
    with wave.open(str(path), "wb") as wav_out:
        wav_out.setnchannels(1)
        wav_out.setsampwidth(2)
        wav_out.setframerate(framerate)
        wav_out.writeframes(b"\x00\x00" * duration_frames)


def _local_work_dir() -> Path:
    base = Path.cwd() / "tests_runtime"
    base.mkdir(parents=True, exist_ok=True)
    work = base / uuid4().hex
    work.mkdir(parents=True, exist_ok=False)
    return work


def test_merge_wav_files() -> None:
    work_dir = _local_work_dir()
    a = work_dir / "a.wav"
    b = work_dir / "b.wav"
    out = work_dir / "out.wav"
    _write_wav(a, duration_frames=1000)
    _write_wav(b, duration_frames=2000)

    merge_wav_files([a, b], out)

    with wave.open(str(out), "rb") as wav_in:
        assert wav_in.getnframes() == 3000


def test_merge_wav_files_rejects_incompatible_files() -> None:
    work_dir = _local_work_dir()
    a = work_dir / "a.wav"
    b = work_dir / "b.wav"
    out = work_dir / "out.wav"
    _write_wav(a, framerate=22050)
    _write_wav(b, framerate=16000)

    with pytest.raises(ValueError):
        merge_wav_files([a, b], out)
