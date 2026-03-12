# PDF_TTs_Ai_Model

Lokalny pipeline PDF -> audio (TTS), z naciskiem na poprawna kolejnosc i logiczne chunkowanie.

## Struktura
- `docs/IMPLEMENTATION_PLAN.md` - plan etapow i gate testow.
- `src/pdf_tts_ai/extractor.py` - ekstrakcja tekstu z PDF.
- `src/pdf_tts_ai/segmenter.py` - podzial tekstu na logiczne chunki.
- `src/pdf_tts_ai/tts.py` - adapter do Piper CLI.
- `src/pdf_tts_ai/audio.py` - scalanie WAV.
- `src/pdf_tts_ai/pipeline.py` - orchestracja end-to-end.
- `src/pdf_tts_ai/service.py` - wspolna logika walidacji i uruchamiania joba.
- `src/pdf_tts_ai/paths.py` - polityka katalogu wyjsciowego (`<base>/<nazwa_pdf>/`).
- `src/pdf_tts_ai/app/` - warstwa uruchomieniowa (CLI/GUI/bootstrap).
- `src/pdf_tts_ai/cli.py` i `src/pdf_tts_ai/gui.py` - cienkie entrypointy.
- `tests/` - testy modulowe.

## Instalacja
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .[dev]
```

`requirements.txt` zawiera runtime dependencies dla prostego onboardingu.

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
- `out/<nazwa_pdf>/chunks/0001.wav`, `0002.wav`, ...
- `out/<nazwa_pdf>/full.wav`
- `out/<nazwa_pdf>/manifest.json`

## GUI
```powershell
python -m pdf_tts_ai.gui
```

GUI pozwala wybrac:
- PDF
- model Piper (`.onnx`)
- katalog bazowy zapisu

Aplikacja tworzy automatycznie folder nazwany jak PDF i zapisuje tam caly wynik.

## Auto-check dependencies
- Przy starcie CLI i GUI aplikacja sprawdza wymagane paczki Pythona.
- Jesli czegos brakuje, uruchamia automatycznie `pip install` dla brakujacych elementow.
- Dla `piper` wyswietlane jest ostrzezenie, jesli nie ma go w `PATH`.
