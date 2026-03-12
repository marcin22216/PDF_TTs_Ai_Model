from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .bootstrap import (
    ensure_onnxruntime_for_hardware,
    has_nvidia_gpu,
    is_cuda_provider_available,
    is_ffmpeg_available,
)
from .config import PipelineConfig
from .extractor import extract_toc, get_page_count
from .models import TocEntry
from .paths import build_document_output_dir
from .pipeline import run_pipeline
from .selection import pages_from_toc_selection, parse_range_expression
from .tts import PiperTTS


@dataclass(slots=True)
class JobRequest:
    pdf_path: Path
    output_base_dir: Path
    model_path: Path
    page_range: str = ""
    chapter_range: str = ""
    piper_exe: str = "piper"
    use_cuda: bool = False
    output_format: str = "wav"
    audio_bitrate: str = "64k"
    delete_temp_wav_chunks: bool = True
    ffmpeg_exe: str = "ffmpeg"
    min_chars: int = 700
    max_chars: int = 1600
    merged_filename: str = "full.wav"
    speaker_id: int | None = None
    length_scale: float | None = None


def validate_request(request: JobRequest) -> None:
    if not request.pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {request.pdf_path}")
    if request.pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF")
    if not request.model_path.exists():
        raise FileNotFoundError(f"TTS model not found: {request.model_path}")
    if request.min_chars <= 0 or request.max_chars <= 0:
        raise ValueError("min_chars and max_chars must be positive")
    if request.min_chars > request.max_chars:
        raise ValueError("min_chars cannot exceed max_chars")
    if request.output_format.lower() not in {"wav", "mp3", "m4a", "ogg"}:
        raise ValueError("output_format must be one of: wav, mp3, m4a, ogg")


def list_toc_entries(pdf_path: Path) -> list[TocEntry]:
    return extract_toc(pdf_path)


def resolve_selected_pages(request: JobRequest) -> list[int]:
    total_pages = get_page_count(request.pdf_path)
    pages = set(parse_range_expression(request.page_range, total_pages))

    if request.chapter_range.strip():
        toc_entries = extract_toc(request.pdf_path)
        chapter_pages = set(
            pages_from_toc_selection(
                toc_entries=toc_entries,
                chapter_selection=request.chapter_range,
                total_pages=total_pages,
            )
        )
        pages = pages.intersection(chapter_pages)

    if not pages:
        raise ValueError("Selected page/chapter ranges produced an empty page set")
    return sorted(pages)


def run_job(
    request: JobRequest,
    *,
    runner: Callable = run_pipeline,
    tts_factory: Callable = PiperTTS,
    progress_callback: Callable[[int, str], None] | None = None,
) -> dict[str, Path]:
    validate_request(request)
    ensure_onnxruntime_for_hardware(auto_install=True)

    use_cuda = request.use_cuda and has_nvidia_gpu() and is_cuda_provider_available()
    output_format = request.output_format.lower()
    if output_format != "wav" and not is_ffmpeg_available(request.ffmpeg_exe):
        raise RuntimeError(
            f"Output format '{output_format}' requires ffmpeg. "
            f"Install ffmpeg or switch output format to 'wav'."
        )

    out_dir = build_document_output_dir(request.output_base_dir, request.pdf_path)
    selected_pages = resolve_selected_pages(request)
    config = PipelineConfig(
        pdf_path=request.pdf_path,
        out_dir=out_dir,
        selected_pages=selected_pages,
        min_chars=request.min_chars,
        max_chars=request.max_chars,
        merged_filename=request.merged_filename,
        output_format=output_format,
        audio_bitrate=request.audio_bitrate,
        delete_temp_wav_chunks=request.delete_temp_wav_chunks,
        ffmpeg_exe=request.ffmpeg_exe,
    )
    tts_engine = tts_factory(
        model_path=request.model_path,
        piper_exe=request.piper_exe,
        use_cuda=use_cuda,
        speaker_id=request.speaker_id,
        length_scale=request.length_scale,
    )
    if progress_callback is None:
        return runner(config=config, tts_engine=tts_engine)
    return runner(config=config, tts_engine=tts_engine, progress_callback=progress_callback)
