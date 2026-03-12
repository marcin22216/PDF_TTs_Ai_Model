from pathlib import Path
import shutil
import subprocess
import wave


def merge_wav_files(input_paths: list[Path], output_path: Path) -> None:
    if not input_paths:
        raise ValueError("No input WAV files to merge")

    params = None
    frames: list[bytes] = []
    for path in input_paths:
        with wave.open(str(path), "rb") as wav_in:
            if params is None:
                params = wav_in.getparams()
            else:
                current = wav_in.getparams()
                if (
                    current.nchannels != params.nchannels
                    or current.sampwidth != params.sampwidth
                    or current.framerate != params.framerate
                    or current.comptype != params.comptype
                    or current.compname != params.compname
                ):
                    raise ValueError("Incompatible WAV files for merge")
            frames.append(wav_in.readframes(wav_in.getnframes()))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_out:
        wav_out.setparams(params)
        for data in frames:
            wav_out.writeframes(data)


def transcode_audio(
    input_path: Path,
    output_path: Path,
    *,
    output_format: str,
    bitrate: str,
    ffmpeg_exe: str = "ffmpeg",
) -> None:
    if output_format == "wav":
        shutil.copyfile(input_path, output_path)
        return

    codec_args_map = {
        "mp3": ["-c:a", "libmp3lame", "-b:a", bitrate],
        "m4a": ["-c:a", "aac", "-b:a", bitrate],
        "ogg": ["-c:a", "libvorbis", "-b:a", bitrate],
    }
    if output_format not in codec_args_map:
        raise ValueError(f"Unsupported output format: {output_format}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(input_path),
        *codec_args_map[output_format],
        str(output_path),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffmpeg executable not found. Install ffmpeg or use output format 'wav'."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
        raise RuntimeError(f"ffmpeg conversion failed: {stderr}") from exc
