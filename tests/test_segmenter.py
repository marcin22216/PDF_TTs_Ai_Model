from pdf_tts_ai.models import TextBlock
from pdf_tts_ai.segmenter import build_chunks


def test_build_chunks_respects_limits_and_order() -> None:
    blocks = [
        TextBlock(page=1, text="Pierwsze zdanie. Drugie zdanie. Trzecie zdanie."),
        TextBlock(page=2, text="Czwarte zdanie. Piąte zdanie."),
    ]

    chunks = build_chunks(blocks, min_chars=20, max_chars=40)

    assert chunks
    assert [c.index for c in chunks] == list(range(1, len(chunks) + 1))
    assert all(len(c.text) <= 40 for c in chunks)
    assert all(c.text[-1] in ".!?" or len(c.text) == 40 for c in chunks)
    assert chunks[0].page_start == 1
    assert chunks[-1].page_end == 2
