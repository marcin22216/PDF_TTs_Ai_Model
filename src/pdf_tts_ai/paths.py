from pathlib import Path
import re

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
MULTI_UNDERSCORE = re.compile(r"_+")


def sanitize_pdf_stem(pdf_path: Path) -> str:
    stem = pdf_path.stem.strip()
    if not stem:
        return "document"

    cleaned = INVALID_FILENAME_CHARS.sub("_", stem)
    cleaned = cleaned.replace(" ", "_")
    cleaned = MULTI_UNDERSCORE.sub("_", cleaned).strip("._")
    return cleaned or "document"


def build_document_output_dir(base_dir: Path, pdf_path: Path) -> Path:
    target = base_dir / sanitize_pdf_stem(pdf_path)
    target.mkdir(parents=True, exist_ok=True)
    return target
