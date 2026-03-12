import re

from .models import Chunk, TextBlock

SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+")
SOFT_SPLIT_REGEX = re.compile(r"(?<=[,;:])\s+")
WHITESPACE_REGEX = re.compile(r"\s+")
HEADING_TOKEN_REGEX = re.compile(r"^(rozdzial|chapter|kapitel|[ivxlcdm]+\.)\b", re.IGNORECASE)


def _is_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped) > 90:
        return False
    if stripped.endswith((".", "!", "?", ";", ":")):
        return False

    words = [w for w in re.split(r"\s+", stripped) if w]
    if not words:
        return False

    if HEADING_TOKEN_REGEX.match(stripped):
        return True

    alpha_ratio = sum(ch.isalpha() for ch in stripped) / max(1, len(stripped))
    title_case_ratio = sum(1 for w in words if w[0:1].isupper()) / len(words)
    is_upper = stripped.upper() == stripped and any(ch.isalpha() for ch in stripped)
    return alpha_ratio > 0.6 and (is_upper or title_case_ratio > 0.7)


def _prepare_text_for_tts_segmentation(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    prepared: list[str] = []
    for line in lines:
        if not line:
            prepared.append("")
            continue
        if _is_heading_line(line):
            prepared.append(f"{line}.")
            prepared.append("")  # extra pause after heading/title
        else:
            prepared.append(line)
    return "\n".join(prepared)


def normalize_text(text: str) -> str:
    return WHITESPACE_REGEX.sub(" ", text).strip()


def split_sentences(text: str) -> list[str]:
    prepared = _prepare_text_for_tts_segmentation(text)
    normalized = normalize_text(prepared)
    if not normalized:
        return []
    return [s.strip() for s in SENTENCE_SPLIT_REGEX.split(normalized) if s.strip()]


def _split_long_sentence(sentence: str, max_chars: int) -> list[str]:
    if len(sentence) <= max_chars:
        return [sentence]

    parts = [p.strip() for p in SOFT_SPLIT_REGEX.split(sentence) if p.strip()]
    if len(parts) > 1:
        merged: list[str] = []
        current = ""
        for part in parts:
            candidate = f"{current} {part}".strip()
            if current and len(candidate) > max_chars:
                merged.append(current)
                current = part
            else:
                current = candidate
        if current:
            merged.append(current)
        return merged

    words = sentence.split(" ")
    merged = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            merged.append(current)
            current = word
        else:
            current = candidate
    if current:
        merged.append(current)
    return merged


def build_chunks(blocks: list[TextBlock], min_chars: int, max_chars: int) -> list[Chunk]:
    if min_chars <= 0 or max_chars <= 0:
        raise ValueError("min_chars and max_chars must be positive")
    if min_chars > max_chars:
        raise ValueError("min_chars cannot exceed max_chars")

    chunks: list[Chunk] = []
    chunk_index = 1
    current_text = ""
    current_page_start: int | None = None
    current_page_end: int | None = None

    def flush_current() -> None:
        nonlocal chunk_index, current_text, current_page_start, current_page_end
        if not current_text:
            return
        chunks.append(
            Chunk(
                index=chunk_index,
                page_start=current_page_start or 1,
                page_end=current_page_end or current_page_start or 1,
                text=current_text.strip(),
            )
        )
        chunk_index += 1
        current_text = ""
        current_page_start = None
        current_page_end = None

    for block in blocks:
        for sentence in split_sentences(block.text):
            for piece in _split_long_sentence(sentence, max_chars=max_chars):
                if current_page_start is None:
                    current_page_start = block.page
                current_page_end = block.page

                candidate = f"{current_text} {piece}".strip()
                if current_text and len(candidate) > max_chars:
                    flush_current()
                    current_page_start = block.page
                    current_page_end = block.page
                    current_text = piece
                    continue

                current_text = candidate
                if len(current_text) >= min_chars:
                    flush_current()

    flush_current()
    return chunks
