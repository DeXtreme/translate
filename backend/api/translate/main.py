import os
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any
from .ports import TextPersistencePort, TranslationPort, DynamoDBPersistencePort, AWSTranslatePort

logger = logging.getLogger(__name__)


@dataclass
class TranslationRequest:
    """Dataclass for translation requests"""

    text: str
    lang: str

    @classmethod
    def from_dict(cls, data: Dict[str:Any]) -> "TranslationRequest":
        if not isinstance(data["text"], str):
            raise ValueError("text must be a string")

        if not isinstance(data["lang"], str):
            raise ValueError("lang must be a string")

        return cls(data.get("text"), data.get("lang"))


class Handler:

    def __init__(
        self,
        text_port: TextPersistencePort,
        translate_port: TranslationPort,
    ):

        self.text_port = text_port
        self.translate_port = translate_port

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
            result = self.translate_port.translate(request.text, request.lang)

            output = self.text_port.save(request.text, result)
            logger.info(f"Saved record with ID: {output.id}")

            return self._get_success_response(result)
        except Exception as e:
            return self._get_error_response("An error was encountered", status_code=500)

    def _get_success_response(self, text: str):
        """
        Generate a successful response.

        Args:
            text: The translated text

        Returns:
            Dictionary with status code and response body
        """

        return {"statusCode": "200", "body": json.dumps({"result": text})}

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


text_port = DynamoDBPersistencePort(os.environ.get("DYNAMODB_TABLE"))
translate_port = AWSTranslatePort()

handler = Handler(text_port,translate_port)