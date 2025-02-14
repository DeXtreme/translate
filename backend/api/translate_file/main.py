import os
import json
import base64
import logging
from dataclasses import dataclass
from typing import Dict, Any, Tuple
from requests_toolbelt import MultipartDecoder

from ports import RequestPersistencePort, FilePersistencePort, TranslationPort
from adapters import (
    RequestPersistenceAdapter,
    FilePersistenceAdpater,
    AWSTranslateAdapter,
)

logger = logging.getLogger(__name__)


@dataclass
class TranslationRequest:
    """Dataclass for translation requests"""

    files: list
    lang: str

    @staticmethod
    def get_name(header: bytes) -> str:
        return header.decode().split(";")[1].split("=")[1].strip('"')

    @staticmethod
    def get_file_info(header: bytes) -> Tuple[str, str]:
        filename, extension = None, None
        if len(header.decode().split(";")) >= 3:
            filename = header.decode().split(";")[2].split("=")[1].strip('"')
            file_ext = filename.split(".")
            if len(file_ext) == 2:
                extension = file_ext[1]

        return filename, extension

    @classmethod
    def from_dict(cls, data: Dict) -> "TranslationRequest":
        body = data["body"]
        content_type = data["headers"].get("content-type", None) or data[
            "headers"].get("Content-Type", None)

        files = []
        lang = ""

        if data["isBase64Encoded"]:
            body = base64.b64decode(body)

        decoder = MultipartDecoder(body, content_type)
        for part in decoder.parts:
            filename, extension = cls.get_file_info(
                part.headers[b"Content-Disposition"]
            )
            if filename:
                content_type = part.headers[b"content-type"].decode()
                files.append((part.content, content_type, extension))
            elif cls.get_name(part.headers[b"Content-Disposition"]) == "lang":
                lang = part.content.decode()

        if not files:
            raise ValueError("files must be provided")

        if not lang:
            raise ValueError("lang must be a string")

        return cls(files, lang)


class Handler:

    def __init__(
        self,
        request_port: RequestPersistencePort,
        file_port: FilePersistencePort,
        translate_port: TranslationPort,
    ):

        self.request_port = request_port
        self.translate_port = translate_port
        self.file_port = file_port

    def __call__(self, request, *args):
        """
        Process a translation request.

        Args:
            request: dict containing the request data

        Returns:
            dict with status code and response body
        """

        try:
            request = TranslationRequest.from_dict(request)
        except (json.JSONDecodeError, KeyError) as e:
            logger.exception(f"Invalid request: {str(e)}")
            return self._get_error_response("Invalid request", status_code=400)

        urls = []
        try:
            lang = request.lang
            for file in request.files:
                result = self.translate_port.translate(file[0], file[1], lang)
                output = self.request_port.save(file[0], result)
                logger.info(f"Saved record with ID: {output.id}")

                url = self.file_port.save(result, file[2])
                urls.append(url)

            return self._get_success_response(urls)
        except Exception as e:
            logger.exception(f"Error translating: {str(e)}")
            return self._get_error_response("An error was encountered", status_code=500)

    def _get_success_response(self, urls: list):
        """
        Generate a successful response.

        Args:
            url: Path to the output file

        Returns:
            Dictionary with status code and response body
        """

        return {"statusCode": "200", 
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"urls": urls})}

    def _get_error_response(self, error: str, status_code: int):
        """
        Generate an error response.

        Args:
            error: The error message
            status_code: HTTP status code

        Returns:
            Dictionary with status code and response body
        """

        return {"statusCode": str(status_code),
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"detail": error})}


request_port = RequestPersistenceAdapter(os.environ.get("DYNAMODB_TABLE"))
file_port = FilePersistenceAdpater(os.environ.get("S3_BUCKET"))
translate_port = AWSTranslateAdapter()

handler = Handler(request_port, file_port, translate_port)
