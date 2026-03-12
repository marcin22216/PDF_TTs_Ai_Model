# PDF_TTs_Ai_Model - Przewodnik Startowy (PL)

Ten plik jest dla nowego uzytkownika, ktory pobral projekt jako ZIP z GitHub i chce uruchomic aplikacje od zera.

## 1. Wymagania
- Windows 10/11
- Python 3.10+ (zalecane 3.12)
- Internet do pierwszej instalacji paczek i modelu

## 2. Rozpakowanie projektu
1. Pobierz ZIP repozytorium z GitHub.
2. Rozpakuj, np. do:
`C:\Users\<twoj_uzytkownik>\Documents\PDF_TTs_Ai_Model`

## 3. Uruchom PowerShell w folderze projektu
W PowerShell przejdz do folderu:

```powershell
cd C:\Users\marci\Documents\VSCode\PDF_TTs_Ai_Model
```

## 4. Utworz i aktywuj srodowisko wirtualne
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 5. Zainstaluj zaleznosci projektu
```powershell
python -m pip install -U pip
python -m pip install -e .[dev]
python -m pip install piper-tts pathvalidate
```

## 6. Pobierz polski model TTS (Piper)
```powershell
New-Item -ItemType Directory -Force .\models | Out-Null
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx" -OutFile ".\models\pl_PL-gosia-medium.onnx"
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json" -OutFile ".\models\pl_PL-gosia-medium.onnx.json"
```

Sprawdz, czy pliki sa:
```powershell
Get-ChildItem .\models
```

## 7. Szybki test Piper
```powershell
"To jest test syntezy mowy po polsku." | .\.venv\Scripts\piper --model ".\models\pl_PL-gosia-medium.onnx" --output_file ".\test.wav"
```

Jesli powstal `test.wav`, TTS dziala.

## 8. Uruchom GUI
```powershell
python -m pdf_tts_ai.gui
```

W GUI ustaw:
- `PDF file` - plik PDF
- `Piper model` - `.\models\pl_PL-gosia-medium.onnx`
- `Piper executable` - `.\.venv\Scripts\piper.exe`
- `Output base dir` - katalog bazowy, gdzie maja byc wyniki
- opcjonalnie `Use GPU (CUDA)` (patrz sekcja GPU)

Kliknij `Start`.

## 9. Gdzie sa wyniki
Aplikacja zawsze tworzy folder o nazwie pliku PDF:

`<Output base dir>\<nazwa_pdf>\`

W nim:
- `chunks\0001.wav`, `0002.wav`, ...
- `full.wav`
- `manifest.json`

## 10. Uruchomienie bez GUI (CLI)
```powershell
python -m pdf_tts_ai.cli --pdf ".\input.pdf" --out ".\out" --model ".\models\pl_PL-gosia-medium.onnx" --piper-exe ".\.venv\Scripts\piper.exe"
```

## 11. GPU (CUDA) - opcjonalnie
Domyslnie aplikacja dziala na CPU. Zeby uruchomic GPU:

```powershell
python -m pip uninstall -y onnxruntime
python -m pip install onnxruntime-gpu
python -c "import onnxruntime as ort; print(ort.get_available_providers())"
```

Na liscie providerow musi byc:
`CUDAExecutionProvider`

Potem:
- GUI: zaznacz `Use GPU (CUDA)`
- CLI: dodaj flage `--cuda`

## 12. Najczestsze problemy
- `piper executable not found`:
  ustaw `Piper executable` na `.\.venv\Scripts\piper.exe`.
- `CUDAExecutionProvider is unavailable`:
  nie ma aktywnego runtime GPU, zrob kroki z sekcji GPU.
- bledy instalacji pip:
  uruchom PowerShell jako zwykly user, sprawdz internet i powtorz komendy.

## 13. Testy projektu
```powershell
python -m pytest tests
```

Jesli widzisz przechodzace testy, repo jest gotowe do pracy.
