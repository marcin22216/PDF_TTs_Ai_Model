from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .bootstrap import is_cuda_provider_available
from .config import PipelineConfig
from .paths import build_document_output_dir
from .pipeline import run_pipeline
from .tts import PiperTTS


@dataclass(slots=True)
class JobRequest:
    pdf_path: Path
    output_base_dir: Path
    model_path: Path
    piper_exe: str = "piper"
    use_cuda: bool = False
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
    if request.use_cuda and not is_cuda_provider_available():
        raise RuntimeError(
            "CUDA requested, but CUDAExecutionProvider is unavailable in onnxruntime. "
            "Install onnxruntime-gpu and ensure NVIDIA drivers/CUDA runtime are correctly set."
        )


def run_job(
    request: JobRequest,
    *,
    runner: Callable = run_pipeline,
    tts_factory: Callable = PiperTTS,
    progress_callback: Callable[[int, str], None] | None = None,
) -> dict[str, Path]:
    validate_request(request)
    out_dir = build_document_output_dir(request.output_base_dir, request.pdf_path)
    config = PipelineConfig(
        pdf_path=request.pdf_path,
        out_dir=out_dir,
        min_chars=request.min_chars,
        max_chars=request.max_chars,
        merged_filename=request.merged_filename,
    )
    tts_engine = tts_factory(
        model_path=request.model_path,
        piper_exe=request.piper_exe,
        use_cuda=request.use_cuda,
        speaker_id=request.speaker_id,
        length_scale=request.length_scale,
    )
    if progress_callback is None:
        return runner(config=config, tts_engine=tts_engine)
    return runner(config=config, tts_engine=tts_engine, progress_callback=progress_callback)
