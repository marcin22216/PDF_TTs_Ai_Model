from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PipelineConfig:
    pdf_path: Path
    out_dir: Path
    min_chars: int = 700
    max_chars: int = 1600
    merged_filename: str = "full.wav"
    output_format: str = "wav"
    audio_bitrate: str = "64k"
    delete_temp_wav_chunks: bool = True
    ffmpeg_exe: str = "ffmpeg"
