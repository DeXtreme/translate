import boto3
import base64
from uuid import uuid4
from datetime import datetime

from .models import Record


class RequestPersistenceAdapter:
    """
    Implementation of RequestPersistencePort using DynamoDB as storage.
    """

    def __init__(self, table_name: str):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def save(self, input: bytes, output: bytes) -> Record:
        """
        Save input and output byptes to DynamoDB.

        Args:
            input: The input bytes to save
            output: The output bytes to save

        Returns:
            Record object containing saved data
        """

        id = str(uuid4())
        created_at = datetime.now()

        input_text = base64.b64encode(input)
        output_text = base64.b64encode(output)


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


class FilePersistenceAdpater:
    """
    Implementation of FilePersistencePort using S3
    """

    def __init__(self, bucket_name: str):
        self.client = boto3.client("s3")
        self.bucket_name = bucket_name
    

    def save(self, file: bytes) -> str:
        """
        Save file as object in S3 bucket

        Args:
            file: The file to save

        Returns:
            The url to the file
        """

        key = str(uuid4()).replace("-","")

        response = self.client.put_object(
            Key = key,
            Body = file,
            Bucket = self.bucket_name
        )

        url = self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=60
        )

        return url

        

        
class AWSTranslateAdapter:
    """
    Implementation of TranslationPort using AWSTranslate.
    """

    def __init__(self):
        self.client = boto3.client("translate")

    def translate(self, file: bytes, lang: str) -> bytes:
        """
        Translate input file to lang

        Args:
            file: The file to translate
            lang: The language code to translate to

        Returns:
            The translated file
        """


        result = self.client.translate_document(
            Document={
                'Content': file,
                'ContentType': 'text/plain'
            },
            SourceLanguageCode="auto",
            TargetLanguageCode=lang,
        )

        translated_file = result["TranslatedDocument"]["Content"]

        return translated_file
