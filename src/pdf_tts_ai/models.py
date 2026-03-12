from dataclasses import dataclass


@dataclass(slots=True)
class TextBlock:
    page: int
    text: str


@dataclass(slots=True)
class Chunk:
    index: int
    page_start: int
    page_end: int
    text: str

    @property
    def char_count(self) -> int:
        return len(self.text)
