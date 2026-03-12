# PDF -> TTS Local MVP Plan

## Goal
Build a local app that:
1. Reads a PDF in correct order.
2. Splits text into logical chunks (no cut in middle of sentence).
3. Generates audio per chunk.
4. Produces one merged audio file and a manifest with ordering metadata.

## Architecture
- `extractor.py`: deterministic PDF text extraction.
- `segmenter.py`: text cleanup and logical chunking.
- `tts.py`: local TTS adapter (Piper CLI).
- `audio.py`: WAV merge preserving chunk order.
- `pipeline.py`: orchestrates full flow and writes `manifest.json`.
- `cli.py`: command-line entrypoint.

## Delivery Steps With Gate Tests
### Step 1 - Extractor module
- Deliverable: `extract_blocks(pdf_path)` returning page-aware blocks.
- Gate tests:
  - Extracts text from synthetic multi-page PDF.
  - Preserves page numbers.

### Step 2 - Segmenter module
- Deliverable: `build_chunks(blocks, min_chars, max_chars)`.
- Gate tests:
  - No chunk exceeds `max_chars`.
  - Chunk boundaries do not cut sentences in normal cases.
  - Chunk indexes are monotonic.

### Step 3 - Audio merge module
- Deliverable: `merge_wav_files(inputs, output)`.
- Gate tests:
  - Output WAV exists and contains joined frames.
  - Rejects incompatible WAV params.

### Step 4 - Pipeline orchestration
- Deliverable: `run_pipeline(config, tts_engine)`.
- Gate tests:
  - Creates per-chunk WAV files.
  - Creates merged WAV and `manifest.json`.
  - Manifest order matches chunk order.

### Step 5 - CLI
- Deliverable: `python -m pdf_tts_ai.cli ...`.
- Gate tests:
  - `--help` works.
  - Required args validation.

## MVP Scope (Now)
- Text PDFs only (no OCR yet).
- Piper as TTS backend.
- WAV output.

## Next Iterations
- OCR fallback for scanned PDFs.
- Header/footer removal heuristics.
- Optional skip rules (footnotes, bibliography, TOC).
- Parallel chunk synthesis with ordered merge.
