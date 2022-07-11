#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Union

import boto3
from airbyte_cdk.models import AirbyteStream, SyncMode
from pydantic.types import NonNegativeInt
from source_dynamodb import constants as cnst
from source_dynamodb.typing import Spec


class Reader:
    def __init__(self, logger: logging.Logger, config: Spec) -> None:
        self.logger = logger
        self.aws_access_key_id = config["aws_access_key_id"]
        self.aws_secret_access_key = config["aws_secret_access_key"]
        self.region_name = config["region_name"]
        try:
            self.client = boto3.client(
                "dynamodb",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

        try:
            self.service = boto3.resource(
                "dynamodb",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
            )
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

        try:
            response = self.client.list_tables(Limit=1)
            list_of_tables = response["TableNames"]
            return len(list_of_tables)
        except Exception as e:
            raise Exception(f"An exception occured: {str(e)}")

    def get_streams(self) -> List[AirbyteStream]:
        try:
            tables: List[str] = []

            paginator = self.client.get_paginator("list_tables")
            response_iterator = paginator.paginate(
                PaginationConfig={
                    "MaxItems": 1,
                    "PageSize": 1,
                },
            )

            last_evaluated_table: Union[str, None] = None

            for response in response_iterator:
                tables.extend(response["TableNames"])
                last_evaluated_table = response.get("LastEvaluatedTableName")

            while last_evaluated_table:
                response_iterator = paginator.paginate(
                    PaginationConfig={
                        "MaxItems": cnst.MAX_ITEMS_PAGINATOR,
                        "PageSize": cnst.MAX_ITEMS_PAGINATOR,
                        "StartingToken": last_evaluated_table,
                    },
                )

                for response in response_iterator:
                    tables.extend(response["TableNames"])
                    last_evaluated_table = response.get(
                        "LastEvaluatedTableName"
                    )

            streams: List[AirbyteStream] = []
            for table in tables:
                stream = AirbyteStream(
                    name=table,
                    json_schema=self.typed_schema,
                    default_cursor_field=None,
                    source_defined_cursor=None,
                    source_defined_primary_key=None,
                    namespace=None,
                )
                stream.supported_sync_modes = [SyncMode.full_refresh]
                streams.append(stream)
            self.logger.info(f"Total streams founds: {len(streams)}")
            return streams

        except Exception as e:
            raise Exception(f"An excpetion occurred: {str(e)}")

    @property
    def typed_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "additionalProperties": {"type": "boolean"},
            },
        }

    def read(self, table_name: str) -> Iterable:
        try:
            table = self.service.Table(name=table_name)
            response = table.scan()
            data = response["Items"]

            while "LastEvaluatedKey" in response.keys():
                response = table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                data.extend(response["Items"])

            return data
        except Exception as e:
            raise Exception(f"An excpetion occurred: {str(e)}")


if __name__ == "__main__":
    spec = Spec(
        **{
            "aws_access_key_id": "AKIA6BNKWOY4X6YTOPPS",
            "aws_secret_access_key": "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",
            "region_name": "us-east-1",
        }
    )
    rdr = Reader(logger=logging.getLogger("airbyte"), config=spec)
    print((rdr.read(table_name="ProductCatalog")))
