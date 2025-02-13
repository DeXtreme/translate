from typing import Protocol
from models import Record


class RequestPersistencePort(Protocol):
    def save(self, input: bytes, output: bytes) -> Record:
        pass


class FilePersistencePort(Protocol):
    def save(self, file: bytes, extension: str) -> str:
        pass


class TranslationPort(Protocol):
    def translate(self, file: bytes, content_Type: str, lang: str) -> bytes:
        pass
