from pathlib import Path
from typing import Callable, Protocol

from .audio import merge_wav_files
from .config import PipelineConfig
from .extractor import extract_blocks
from .manifest import write_manifest
from .segmenter import build_chunks


class TTSEngine(Protocol):
    def synthesize_to_wav(self, text: str, output_path: Path) -> None:
        ...


ProgressCallback = Callable[[int, str], None]


def run_pipeline(
    config: PipelineConfig,
    tts_engine: TTSEngine,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Path]:
    def report(percent: int, stage: str) -> None:
        if progress_callback is not None:
            progress_callback(percent, stage)

    report(0, "Initializing")
    config.out_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir = config.out_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    report(5, "Extracting text")
    blocks = extract_blocks(config.pdf_path)
    if not blocks:
        raise ValueError("No extractable text found in PDF")

    report(15, "Building chunks")
    chunks = build_chunks(blocks, min_chars=config.min_chars, max_chars=config.max_chars)
    if not chunks:
        raise ValueError("No chunks generated")

    report(20, "Synthesizing audio")
    chunk_audio_paths: list[Path] = []
    total_chunks = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        chunk_path = chunks_dir / f"{chunk.index:04d}.wav"
        tts_engine.synthesize_to_wav(chunk.text, chunk_path)
        chunk_audio_paths.append(chunk_path)
        progress = 20 + int((idx / total_chunks) * 70)
        report(progress, f"Synthesizing chunk {idx}/{total_chunks}")

    report(93, "Merging audio")
    merged_path = config.out_dir / config.merged_filename
    merge_wav_files(chunk_audio_paths, merged_path)

    report(97, "Writing manifest")
    manifest_path = config.out_dir / "manifest.json"
    write_manifest(config.pdf_path, chunks, chunk_audio_paths, manifest_path)
    report(100, "Completed")
    return {"manifest": manifest_path, "merged_audio": merged_path, "chunks_dir": chunks_dir}
