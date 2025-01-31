import boto3
from uuid import uuid4
from datetime import datetime
from typing import Protocol

from .models import Record


class TextPersistencePort(Protocol):
    def save(self, input_text: str, output_text: str) -> Record:
        pass


class TranslationPort(Protocol):
    def translate(self, text: str, lang: str) -> str:
        pass


class DynamoDBPersistencePort:
    """
    Implementation of TextPersistencePort using DynamoDB as storage.
    """

    def __init__(self, table_name: str):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def save(self, input_text, output_text):
        """
        Save input and output text to DynamoDB.

        Args:
            input_text: The input text to save
            output_text: The output text to save

        Returns:
            Record object containing saved data
        """

        id = str(uuid4())
        created_at = datetime.now()

        self.table.put_item(
            Item={
                "id": str(uuid4()),
                "input_text": input_text,
                "output_text": output_text,
                "created_at": str(created_at),
            }
        )

        record = Record(id, input_text, output_text, created_at)
        return record


class AWSTranslatePort:
    """
    Implementation of TranslationPort using DynamoDB as storage.
    """

    def __init__(self):
        self.client = boto3.client("translate")

    def translate(self, text, lang):
        """
        Translate text to lang

        Args:
            text: The text to translate
            lang: The language code to translate to

        Returns:
            The translated string
        """

        result = self.client.translate_text(
            Text=text,
            SourceLanguageCode="auto",
            TargetLanguageCode=lang,
        )

        translated_text = result["TranslatedText"]

        return translated_text
