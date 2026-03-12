from pathlib import Path
import json
from uuid import uuid4
import wave

import fitz

from pdf_tts_ai.config import PipelineConfig
from pdf_tts_ai.pipeline import run_pipeline


class DummyTTS:
    def synthesize_to_wav(self, text: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frames = max(500, len(text) * 5)
        with wave.open(str(output_path), "wb") as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(2)
            wav_out.setframerate(22050)
            wav_out.writeframes(b"\x00\x00" * frames)


def _create_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Ala ma kota. Kot ma Ale. To jest testowy dokument PDF do pipeline.",
    )
    doc.save(path)
    doc.close()


def _local_work_dir() -> Path:
    base = Path.cwd() / "tests_runtime"
    base.mkdir(parents=True, exist_ok=True)
    work = base / uuid4().hex
    work.mkdir(parents=True, exist_ok=False)
    return work


def test_run_pipeline_creates_manifest_and_audio() -> None:
    work_dir = _local_work_dir()
    pdf_path = work_dir / "sample.pdf"
    out_dir = work_dir / "out"
    _create_pdf(pdf_path)

    config = PipelineConfig(pdf_path=pdf_path, out_dir=out_dir, min_chars=20, max_chars=80)
    outputs = run_pipeline(config=config, tts_engine=DummyTTS())

    assert outputs["manifest"].exists()
    assert outputs["merged_audio"].exists()
    assert outputs["chunks_dir"].exists()

    data = json.loads(outputs["manifest"].read_text(encoding="utf-8"))
    assert data["chunks"]
    indices = [c["chunk_index"] for c in data["chunks"]]
    assert indices == sorted(indices)
