from pathlib import Path
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
