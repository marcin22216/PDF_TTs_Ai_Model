from pathlib import Path
import subprocess
import unicodedata
import re
import tempfile
import os


WHITESPACE_REGEX = re.compile(r"\s+")


def _clean_text_for_tts(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    allowed_punctuation = set(".,!?;:-()%/\"'[]")
    cleaned_chars: list[str] = []
    for char in normalized:
        if char.isalnum() or char.isspace() or char in allowed_punctuation:
            cleaned_chars.append(char)
        else:
            cleaned_chars.append(" ")
    return WHITESPACE_REGEX.sub(" ", "".join(cleaned_chars)).strip()


class PiperTTS:
    def __init__(
        self,
        model_path: Path,
        piper_exe: str = "piper",
        use_cuda: bool = False,
        speaker_id: int | None = None,
        length_scale: float | None = None,
    ) -> None:
        self.model_path = model_path
        self.piper_exe = piper_exe
        self.use_cuda = use_cuda
        self.speaker_id = speaker_id
        self.length_scale = length_scale

    def synthesize_to_wav(self, text: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_text = _clean_text_for_tts(text)
        if not cleaned_text:
            raise ValueError("Chunk text is empty after TTS sanitization")

        command = [
            self.piper_exe,
            "--model",
            str(self.model_path),
            "--output_file",
            str(output_path),
        ]
        if self.use_cuda:
            command.append("--cuda")
        if self.speaker_id is not None:
            command.extend(["--speaker", str(self.speaker_id)])
        if self.length_scale is not None:
            command.extend(["--length_scale", str(self.length_scale)])

        temp_input_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as temp_input:
                temp_input.write(cleaned_text)
                temp_input.write("\n")
                temp_input_path = temp_input.name

            command.extend(["--input_file", temp_input_path])
            subprocess.run(
                command,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else ""
            snippet = cleaned_text[:160]
            raise RuntimeError(
                f"Piper synthesis failed (exit={exc.returncode}). "
                f"Text snippet: {snippet!r}. Stderr: {stderr}"
            ) from exc
        finally:
            if temp_input_path:
                try:
                    os.remove(temp_input_path)
                except OSError:
                    pass
