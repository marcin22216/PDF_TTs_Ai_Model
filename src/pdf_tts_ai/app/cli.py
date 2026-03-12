from argparse import ArgumentParser
from pathlib import Path

from .bootstrap import ensure_runtime_dependencies, is_piper_available
from ..service import JobRequest, run_job


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Local PDF to TTS pipeline")
    parser.add_argument("--pdf", type=Path, required=True, help="Path to input PDF")
    parser.add_argument("--out", type=Path, required=True, help="Output base directory")
    parser.add_argument("--model", type=Path, required=True, help="Path to Piper model file")
    parser.add_argument("--piper-exe", default="piper", help="Piper executable path")
    parser.add_argument("--min-chars", type=int, default=700)
    parser.add_argument("--max-chars", type=int, default=1600)
    parser.add_argument("--merged-name", default="full.wav")
    parser.add_argument("--speaker-id", type=int, default=None)
    parser.add_argument("--length-scale", type=float, default=None)
    return parser


def main() -> None:
    ensure_runtime_dependencies(auto_install=True)
    if not is_piper_available():
        print("Warning: 'piper' executable not found in PATH. Use --piper-exe if needed.")

    parser = build_parser()
    args = parser.parse_args()

    request = JobRequest(
        pdf_path=args.pdf,
        output_base_dir=args.out,
        model_path=args.model,
        piper_exe=args.piper_exe,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        merged_filename=args.merged_name,
        speaker_id=args.speaker_id,
        length_scale=args.length_scale,
    )
    outputs = run_job(request)
    print(f"Merged audio: {outputs['merged_audio']}")
    print(f"Manifest: {outputs['manifest']}")


if __name__ == "__main__":
    main()
