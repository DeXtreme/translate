from typing import Protocol
from models import Record


class TextPersistencePort(Protocol):
    def save(self, input_text: str, output_text: str) -> Record:
        pass


class TranslationPort(Protocol):
    def translate(self, text: str, lang: str) -> str:
        pass
