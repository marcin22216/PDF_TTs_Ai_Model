from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PipelineConfig:
    pdf_path: Path
    out_dir: Path
    min_chars: int = 700
    max_chars: int = 1600
    merged_filename: str = "full.wav"
