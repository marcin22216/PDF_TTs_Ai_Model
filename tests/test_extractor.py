from pathlib import Path
from uuid import uuid4

import fitz

from pdf_tts_ai.extractor import extract_blocks, extract_toc, get_page_count


def _create_pdf(path: Path) -> None:
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((72, 72), "To jest strona 1. Pierwsze zdanie.")
    p2 = doc.new_page()
    p2.insert_text((72, 72), "To jest strona 2. Drugie zdanie.")
    p3 = doc.new_page()
    p3.insert_text((72, 72), "To jest strona 3. Trzecie zdanie.")
    doc.set_toc([[1, "Rozdzial 1", 1], [1, "Rozdzial 2", 3]])
    doc.save(path)
    doc.close()


def _create_pdf_with_text_toc(path: Path) -> None:
    doc = fitz.open()
    toc_page = doc.new_page()
    toc_lines = [
        "SPIS TRESCI:",
        "WSTEP ........................................ 4",
        "Czesc I ...................................... 7",
        "Rozdzial I: Awangardowe praktyki ............ 69",
        "Rozdzial II: Gry w awangardzie .............. 142",
    ]
    y = 72
    for line in toc_lines:
        toc_page.insert_text((72, y), line)
        y += 18

    for page_no in range(2, 151):
        page = doc.new_page()
        page.insert_text((72, 72), f"Strona {page_no}")
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

    assert len(blocks) == 3
    assert blocks[0].page == 1
    assert "strona 1" in blocks[0].text
    assert blocks[1].page == 2
    assert "strona 2" in blocks[1].text


def test_extract_blocks_with_page_filter() -> None:
    work_dir = _local_work_dir()
    pdf_path = work_dir / "sample.pdf"
    _create_pdf(pdf_path)
    blocks = extract_blocks(pdf_path, selected_pages={2, 3})
    assert [b.page for b in blocks] == [2, 3]


def test_extract_toc_and_page_count() -> None:
    work_dir = _local_work_dir()
    pdf_path = work_dir / "sample.pdf"
    _create_pdf(pdf_path)

    toc = extract_toc(pdf_path)
    assert len(toc) == 2
    assert toc[0].title == "Rozdzial 1"
    assert toc[1].page == 3
    assert get_page_count(pdf_path) == 3


def test_extract_toc_falls_back_to_text_toc() -> None:
    work_dir = _local_work_dir()
    pdf_path = work_dir / "sample_text_toc.pdf"
    _create_pdf_with_text_toc(pdf_path)

    toc = extract_toc(pdf_path)

    assert len(toc) >= 4
    assert toc[0].title == "WSTEP"
    assert toc[0].page == 4
    assert any(entry.title.startswith("Rozdzial II") and entry.page == 142 for entry in toc)


def test_extract_toc_prefers_outline_over_text_toc() -> None:
    work_dir = _local_work_dir()
    pdf_path = work_dir / "sample_outline_and_text_toc.pdf"
    _create_pdf_with_text_toc(pdf_path)
    with fitz.open(pdf_path) as doc:
        doc.set_toc([[1, "Outline A", 2], [1, "Outline B", 5]])
        doc.saveIncr()

    toc = extract_toc(pdf_path)

    assert [entry.title for entry in toc] == ["Outline A", "Outline B"]
    assert [entry.page for entry in toc] == [2, 5]
