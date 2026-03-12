from pathlib import Path

import fitz

from .models import TextBlock


def extract_blocks(pdf_path: Path) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc, start=1):
            text = page.get_text("text", sort=True).strip()
            if not text:
                continue
            blocks.append(TextBlock(page=page_index, text=text))
    return blocks
