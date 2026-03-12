from pathlib import Path
import subprocess


class PiperTTS:
    def __init__(
        self,
        model_path: Path,
        piper_exe: str = "piper",
        speaker_id: int | None = None,
        length_scale: float | None = None,
    ) -> None:
        self.model_path = model_path
        self.piper_exe = piper_exe
        self.speaker_id = speaker_id
        self.length_scale = length_scale

    def synthesize_to_wav(self, text: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.piper_exe,
            "--model",
            str(self.model_path),
            "--output_file",
            str(output_path),
        ]
        if self.speaker_id is not None:
            command.extend(["--speaker", str(self.speaker_id)])
        if self.length_scale is not None:
            command.extend(["--length_scale", str(self.length_scale)])

        subprocess.run(
            command,
            input=text,
            text=True,
            check=True,
            capture_output=True,
        )
