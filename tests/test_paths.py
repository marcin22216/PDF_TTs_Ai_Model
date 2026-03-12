from pathlib import Path
from uuid import uuid4

from pdf_tts_ai.paths import build_document_output_dir, sanitize_pdf_stem


def _work_dir() -> Path:
    base = Path.cwd() / "tests_runtime"
    base.mkdir(parents=True, exist_ok=True)
    work = base / uuid4().hex
    work.mkdir(parents=True, exist_ok=False)
    return work


def test_sanitize_pdf_stem_handles_invalid_chars() -> None:
    stem = sanitize_pdf_stem(Path("Raport: 2026*03?12.pdf"))
    assert stem == "Raport_2026_03_12"


def test_build_document_output_dir_creates_named_folder() -> None:
    work = _work_dir()
    base_out = work / "exports"
    pdf = work / "Moj dokument.pdf"
    pdf.write_bytes(b"fake")

    out = build_document_output_dir(base_out, pdf)

    assert out.exists()
    assert out.name == "Moj_dokument"
