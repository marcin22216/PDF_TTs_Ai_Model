from argparse import ArgumentParser
from pathlib import Path

from .config import PipelineConfig
from .pipeline import run_pipeline
from .tts import PiperTTS


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Local PDF to TTS pipeline")
    parser.add_argument("--pdf", type=Path, required=True, help="Path to input PDF")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument("--model", type=Path, required=True, help="Path to Piper model file")
    parser.add_argument("--piper-exe", default="piper", help="Piper executable path")
    parser.add_argument("--min-chars", type=int, default=700)
    parser.add_argument("--max-chars", type=int, default=1600)
    parser.add_argument("--merged-name", default="full.wav")
    parser.add_argument("--speaker-id", type=int, default=None)
    parser.add_argument("--length-scale", type=float, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = PipelineConfig(
        pdf_path=args.pdf,
        out_dir=args.out,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        merged_filename=args.merged_name,
    )
    tts = PiperTTS(
        model_path=args.model,
        piper_exe=args.piper_exe,
        speaker_id=args.speaker_id,
        length_scale=args.length_scale,
    )
    outputs = run_pipeline(config, tts)
    print(f"Merged audio: {outputs['merged_audio']}")
    print(f"Manifest: {outputs['manifest']}")


if __name__ == "__main__":
    main()
