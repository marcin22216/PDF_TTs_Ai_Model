from argparse import ArgumentParser
from pathlib import Path

from .bootstrap import (
    ensure_runtime_dependencies,
    has_nvidia_gpu,
    is_cuda_provider_available,
    is_ffmpeg_available,
    is_piper_available,
)
from ..service import JobRequest, run_job


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Local PDF to TTS pipeline")
    parser.add_argument("--pdf", type=Path, required=True, help="Path to input PDF")
    parser.add_argument("--out", type=Path, required=True, help="Output base directory")
    parser.add_argument("--model", type=Path, required=True, help="Path to Piper model file")
    parser.add_argument("--piper-exe", default="piper", help="Piper executable path")
    parser.add_argument("--cuda", action="store_true", help="Use GPU (CUDA) in Piper")
    parser.add_argument("--format", choices=["wav", "mp3", "m4a", "ogg"], default="wav", help="Output audio format")
    parser.add_argument("--bitrate", default="64k", help="Audio bitrate for compressed formats (e.g. 64k, 96k)")
    parser.add_argument("--keep-temp-chunks", action="store_true", help="Keep temporary WAV chunk files after merge")
    parser.add_argument("--ffmpeg-exe", default="ffmpeg", help="ffmpeg executable path (for non-WAV output)")
    parser.add_argument("--min-chars", type=int, default=700)
    parser.add_argument("--max-chars", type=int, default=1600)
    parser.add_argument("--merged-name", default="full.wav")
    parser.add_argument("--speaker-id", type=int, default=None)
    parser.add_argument("--length-scale", type=float, default=None)
    return parser


def main() -> None:
    ensure_runtime_dependencies(auto_install=True)
    parser = build_parser()
    args = parser.parse_args()
    if args.piper_exe == "piper" and not is_piper_available():
        print("Warning: 'piper' executable not found in PATH. Use --piper-exe if needed.")
    if args.cuda and not has_nvidia_gpu():
        print("Warning: CUDA requested but no NVIDIA GPU detected. Falling back to CPU.")
    elif args.cuda and not is_cuda_provider_available():
        print("Warning: CUDA requested but CUDAExecutionProvider unavailable. Falling back to CPU.")
    output_format = args.format
    if output_format != "wav" and not is_ffmpeg_available(args.ffmpeg_exe):
        print("Warning: ffmpeg not found. Falling back to WAV output.")
        output_format = "wav"

    request = JobRequest(
        pdf_path=args.pdf,
        output_base_dir=args.out,
        model_path=args.model,
        piper_exe=args.piper_exe,
        use_cuda=args.cuda,
        output_format=output_format,
        audio_bitrate=args.bitrate,
        delete_temp_wav_chunks=(not args.keep_temp_chunks),
        ffmpeg_exe=args.ffmpeg_exe,
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
