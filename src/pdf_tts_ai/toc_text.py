from __future__ import annotations

import re
from typing import Iterable

from .models import TocEntry

_TOC_HEADER_RE = re.compile(r"^\s*(spis\s+tre[śs]ci|table\s+of\s+contents|contents)\s*:?\s*$", re.IGNORECASE)
_ENTRY_DOTS_RE = re.compile(r"^(?P<title>.+?)\s*\.{2,}\s*(?P<page>\d{1,4})\s*$")
_ENTRY_SPACES_RE = re.compile(r"^(?P<title>.+?)\s{2,}(?P<page>\d{1,4})\s*$")
_DOTS_ONLY_RE = re.compile(r"^\s*\.{2,}\s*(?P<page>\d{1,4})\s*$")


def extract_toc_from_text_pages(
    pages_text: Iterable[str],
    *,
    total_pages: int,
    min_entries: int = 2,
) -> list[TocEntry]:
    lines = _collect_toc_lines(pages_text)
    if not lines:
        return []

    entries: list[TocEntry] = []
    pending_title: tuple[str, int] | None = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            pending_title = None
            continue
        if _TOC_HEADER_RE.match(stripped):
            pending_title = None
            continue

        entry = _parse_entry_line(line)
        if entry is not None:
            title, page, level = entry
            if 1 <= page <= total_pages:
                entries.append(TocEntry(index=len(entries) + 1, level=level, title=title, page=page))
            pending_title = None
            continue

        dots_only_match = _DOTS_ONLY_RE.match(stripped)
        if pending_title is not None and dots_only_match is not None:
            title, level = pending_title
            page = int(dots_only_match.group("page"))
            if 1 <= page <= total_pages:
                entries.append(TocEntry(index=len(entries) + 1, level=level, title=title, page=page))
            pending_title = None
            continue

        if _looks_like_title_prefix(stripped):
            pending_title = (stripped, _level_from_line(line))
        else:
            pending_title = None

    deduped = _dedupe_entries(entries)
    if len(deduped) < min_entries:
        return []
    return deduped


def _collect_toc_lines(pages_text: Iterable[str], max_pages_after_header: int = 4) -> list[str]:
    collected: list[str] = []
    found_header = False
    pages_after_header = 0

    for page_text in pages_text:
        if found_header and pages_after_header > max_pages_after_header:
            break
        lines = page_text.splitlines()
        if not found_header:
            if any(_TOC_HEADER_RE.match(line.strip()) for line in lines):
                found_header = True
                pages_after_header = 0
                collected.extend(lines)
            continue

        collected.extend(lines)
        pages_after_header += 1

    return collected


def _parse_entry_line(line: str) -> tuple[str, int, int] | None:
    stripped = line.strip()
    for pattern in (_ENTRY_DOTS_RE, _ENTRY_SPACES_RE):
        match = pattern.match(stripped)
        if match is None:
            continue
        title = _normalize_title(match.group("title"))
        if len(title) < 2:
            return None
        return title, int(match.group("page")), _level_from_line(line)
    return None


def _normalize_title(raw_title: str) -> str:
    title = raw_title.strip()
    title = re.sub(r"\s+", " ", title)
    title = title.rstrip(". ").strip()
    return title


def _looks_like_title_prefix(stripped_line: str) -> bool:
    if len(stripped_line) < 2 or stripped_line.isdigit():
        return False
    return not stripped_line.endswith(".")


def _level_from_line(line: str) -> int:
    indent = len(line) - len(line.lstrip(" "))
    return 1 + min(5, indent // 2)


def _dedupe_entries(entries: list[TocEntry]) -> list[TocEntry]:
    deduped: list[TocEntry] = []
    seen: set[tuple[str, int]] = set()
    for entry in entries:
        key = (entry.title.lower(), entry.page)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(TocEntry(index=len(deduped) + 1, level=entry.level, title=entry.title, page=entry.page))
    return deduped
