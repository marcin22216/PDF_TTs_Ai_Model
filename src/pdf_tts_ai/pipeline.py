from pathlib import Path
from typing import Protocol

from .audio import merge_wav_files
from .config import PipelineConfig
from .extractor import extract_blocks
from .manifest import write_manifest
from .segmenter import build_chunks


class TTSEngine(Protocol):
    def synthesize_to_wav(self, text: str, output_path: Path) -> None:
        ...


def run_pipeline(config: PipelineConfig, tts_engine: TTSEngine) -> dict[str, Path]:
    config.out_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir = config.out_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    blocks = extract_blocks(config.pdf_path)
    if not blocks:
        raise ValueError("No extractable text found in PDF")

    chunks = build_chunks(blocks, min_chars=config.min_chars, max_chars=config.max_chars)
    if not chunks:
        raise ValueError("No chunks generated")

    chunk_audio_paths: list[Path] = []
    for chunk in chunks:
        chunk_path = chunks_dir / f"{chunk.index:04d}.wav"
        tts_engine.synthesize_to_wav(chunk.text, chunk_path)
        chunk_audio_paths.append(chunk_path)

    merged_path = config.out_dir / config.merged_filename
    merge_wav_files(chunk_audio_paths, merged_path)

    manifest_path = config.out_dir / "manifest.json"
    write_manifest(config.pdf_path, chunks, chunk_audio_paths, manifest_path)
    return {"manifest": manifest_path, "merged_audio": merged_path, "chunks_dir": chunks_dir}
