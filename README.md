# PDF_TTs_Ai_Model

Lokalny pipeline PDF -> audio (TTS), z naciskiem na poprawna kolejnosc i logiczne chunkowanie.

## Struktura
- `docs/IMPLEMENTATION_PLAN.md` - plan etapow i gate testow.
- `src/pdf_tts_ai/extractor.py` - ekstrakcja tekstu z PDF.
- `src/pdf_tts_ai/segmenter.py` - podzial tekstu na logiczne chunki.
- `src/pdf_tts_ai/tts.py` - adapter do Piper CLI.
- `src/pdf_tts_ai/audio.py` - scalanie WAV.
- `src/pdf_tts_ai/pipeline.py` - orchestracja end-to-end.
- `src/pdf_tts_ai/cli.py` - uruchamianie z terminala.
- `tests/` - testy modulowe.

## Instalacja
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .[dev]
```

## Testy
```powershell
pytest
```

## Uruchomienie
Wymaga lokalnie zainstalowanego `piper` i modelu glosu (`.onnx`).

```powershell
python -m pdf_tts_ai.cli `
  --pdf .\input.pdf `
  --out .\out `
  --model .\models\voice.onnx `
  --min-chars 700 `
  --max-chars 1600
```

Wynik:
- `out/chunks/0001.wav`, `0002.wav`, ...
- `out/full.wav`
- `out/manifest.json`
