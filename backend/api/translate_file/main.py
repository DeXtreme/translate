import os
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any

from .ports import RequestPersistencePort, FilePersistencePort, TranslationPort
from .adapters import RequestPersistenceAdapter, FilePersistenceAdpater, AWSTranslateAdapter

logger = logging.getLogger(__name__)


@dataclass
class TranslationRequest:
    """Dataclass for translation requests"""

    file: str
    lang: str

    @classmethod
    def from_dict(cls, data: Dict[str:Any]) -> "TranslationRequest":
        if not isinstance(data["file"], str):
            raise ValueError("text must be a string")

        if not isinstance(data["lang"], str):
            raise ValueError("lang must be a string")

        return cls(data.get("file"), data.get("lang"))


class Handler:

    def __init__(
        self,
        request_port: RequestPersistencePort,
        file_port: FilePersistencePort,
        translate_port: TranslationPort
    ):

        self.request_port = request_port
        self.translate_port = translate_port
        self.file_port = file_port

    def __call__(self, request):
        """
        Process a translation request.

        Args:
            request: dict containing the request data

        Returns:
            dict with status code and response body
        """

        try:
            body: dict = json.loads(request["body"])
            request = TranslationRequest.from_dict(body)
        except (json.JSONDecodeError, KeyError):
            logger.error(f"Invalid request: {str(e)}")
            return self._get_error_response("Invalid request", status_code=400)

        try:
            result = self.translate_port.translate(request.file, request.lang)
            output = self.request_port.save(request.file, result)
            logger.info(f"Saved record with ID: {output.id}")

            url = self.file_port.save(result)

            return self._get_success_response(url)
        except Exception as e:
            return self._get_error_response("An error was encountered", status_code=500)

    def _get_success_response(self, url: str):
        """
        Generate a successful response.

        Args:
            url: Path to the output file

        Returns:
            Dictionary with status code and response body
        """

        return {"statusCode": "200", "body": json.dumps({"url": url})}

    def _get_error_response(self, error: str, status_code: int):
        """
        Generate an error response.

        Args:
            error: The error message
            status_code: HTTP status code

        Returns:
            Dictionary with status code and response body
        """

        return {"statusCode": str(status_code), "body": json.dumps({"detail": error})}


request_port = RequestPersistencePort(os.environ.get("DYNAMODB_TABLE"))
file_port = FilePersistenceAdpater(os.environ.get("S#_BUCKET"))
translate_port = AWSTranslateAdapter()

handler = Handler(request_port,file_port,translate_port)