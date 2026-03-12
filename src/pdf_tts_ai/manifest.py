import json
from pathlib import Path

from .models import Chunk


def write_manifest(
    doc_path: Path,
    chunks: list[Chunk],
    chunk_audio_paths: list[Path | None],
    output_path: Path,
) -> None:
    payload = {
        "source_pdf": str(doc_path),
        "chunks": [
            {
                "chunk_index": chunk.index,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "char_count": chunk.char_count,
                "text": chunk.text,
                "audio_path": str(audio_path) if audio_path else None,
            }
            for chunk, audio_path in zip(chunks, chunk_audio_paths, strict=True)
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
