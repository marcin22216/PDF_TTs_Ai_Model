MODELE TTS (Piper) - szybki start

Ten katalog nie przechowuje modelu w Git.
Model pobierasz lokalnie skryptem z menu:

1) Dwuklik:
   download_gosia.bat

2) Terminal PowerShell:
   powershell -ExecutionPolicy Bypass -File .\models\download_gosia.ps1 -OutDir .\models

3) Terminal z presetem (bez menu):
   powershell -ExecutionPolicy Bypass -File .\models\download_gosia.ps1 -OutDir .\models -Preset 1
   (Presety: 1=PL Gosia, 2=EN Amy, 3=EN Joe, 4=DE Eva K, 5=DE Thorsten)

Skrypt obsluguje:
- Polski: Gosia
- Angielski: Amy (female), Joe (male)
- Niemiecki: Eva K (female), Thorsten (male)

Repo modeli:
https://huggingface.co/rhasspy/piper-voices
