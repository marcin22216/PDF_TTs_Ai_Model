from pathlib import Path
from uuid import uuid4

import fitz

from pdf_tts_ai.extractor import extract_blocks


def _create_pdf(path: Path) -> None:
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((72, 72), "To jest strona 1. Pierwsze zdanie.")
    p2 = doc.new_page()
    p2.insert_text((72, 72), "To jest strona 2. Drugie zdanie.")
    doc.save(path)
    doc.close()


def _local_work_dir() -> Path:
    base = Path.cwd() / "tests_runtime"
    base.mkdir(parents=True, exist_ok=True)
    work = base / uuid4().hex
    work.mkdir(parents=True, exist_ok=False)
    return work


def test_extract_blocks_reads_pages() -> None:
    work_dir = _local_work_dir()
    pdf_path = work_dir / "sample.pdf"
    _create_pdf(pdf_path)

    blocks = extract_blocks(pdf_path)

    assert len(blocks) == 2
    assert blocks[0].page == 1
    assert "strona 1" in blocks[0].text
    assert blocks[1].page == 2
    assert "strona 2" in blocks[1].text
