from pathlib import Path

import fitz

from .models import TextBlock, TocEntry
from .toc_text import extract_toc_from_text_pages


def get_page_count(pdf_path: Path) -> int:
    with fitz.open(pdf_path) as doc:
        return len(doc)


def extract_toc(pdf_path: Path) -> list[TocEntry]:
    with fitz.open(pdf_path) as doc:
        raw_toc = doc.get_toc()
        outline_entries = _toc_from_outline(raw_toc)
        if outline_entries:
            return outline_entries

        scan_pages = min(len(doc), 20)
        pages_text = [doc[i].get_text("text", sort=True) for i in range(scan_pages)]
        return extract_toc_from_text_pages(pages_text, total_pages=len(doc))


def extract_blocks(pdf_path: Path, selected_pages: set[int] | None = None) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc, start=1):
            if selected_pages is not None and page_index not in selected_pages:
                continue
            text = page.get_text("text", sort=True).strip()
            if not text:
                continue
            blocks.append(TextBlock(page=page_index, text=text))
    return blocks


def _toc_from_outline(raw_toc: list[list]) -> list[TocEntry]:
    entries: list[TocEntry] = []
    idx = 1
    for row in raw_toc:
        if len(row) < 3:
            continue
        level, title, page = row[0], row[1], row[2]
        if not isinstance(page, int) or page < 1:
            continue
        entries.append(TocEntry(index=idx, level=int(level), title=str(title).strip(), page=page))
        idx += 1
    return entries
