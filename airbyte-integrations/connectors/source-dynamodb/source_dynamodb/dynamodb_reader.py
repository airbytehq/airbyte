from __future__ import annotations

import boto3
from airbyte_cdk import AirbyteLogger
from mypy_boto3_dynamodb import DynamoDBClient, DynamoDBServiceResource
from pydantic.types import NonNegativeInt
from source_dynamodb.typing import Spec


class Reader:
    def __init__(self, logger: AirbyteLogger, config: Spec) -> None:
        self.logger = logger
        self.aws_access_key_id = config["aws_access_key_id"]
        self.aws_secret_access_key = config["aws_secret_access_key"]
        self.region_name = config["region_name"]

    def client(self) -> DynamoDBClient:
        try:
            client = boto3.client(
                "dynamodb",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
            return client
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

    def service_resource(self) -> DynamoDBServiceResource:
        try:
            service = boto3.resource(
                "dynamodb",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
            return service
        except Exception as e:
            raise Exception(f"An exception occured: {str(e)}")

    def check(self) -> NonNegativeInt:
        """
        Checks if tables can be reached in DynamoDB

        Raises:
            Exception: Any exception that may occured during the code execution

        Returns:
            NonNegativeInt: Number of reached tables.
        """
        client = self.client()
        try:
            response = client.list_tables(Limit=1)
            list_of_tables = response["TableNames"]
            return len(list_of_tables)
        except Exception as e:
            raise Exception(f"An exception occured: {str(e)}")
