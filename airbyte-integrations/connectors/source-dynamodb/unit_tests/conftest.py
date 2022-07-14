#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import pathlib
from decimal import Decimal
from typing import Any, Dict
from unittest.mock import MagicMock

import boto3
import pytest
from source_dynamodb import reader, source


@pytest.fixture(scope="module")
def credentials() -> Dict[str, str]:
    pwd = pathlib.Path()
    with open(pwd.parent / "secrets/config.json") as file:
        creds = json.load(file)
    return creds


class DynamoDBManager:
    def __init__(self, secrets: Dict[str, Any]) -> None:

        try:
            self.client = boto3.client("dynamodb", **secrets)
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

        try:
            self.service = boto3.resource("dynamodb", **secrets)
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")


@pytest.fixture(scope="module")
def mock_logger() -> MagicMock:
    logger_mock = MagicMock()
    return logger_mock


@pytest.fixture(scope="module")
def my_reader(credentials, mock_logger) -> reader.Reader:

    rdr = reader.Reader(logger=mock_logger, config=credentials)
    return rdr


@pytest.fixture(scope="module")
def my_source(credentials, mock_logger) -> source.SourceDynamodb:
    air_dynamodb = source.SourceDynamodb()
    return air_dynamodb


@pytest.fixture(scope="module")
def populate_table(credentials):
    manager = DynamoDBManager(secrets=credentials)
    manager.service.create_table(
        TableName="Devices",
        KeySchema=[
            {
                "AttributeName": "device_id",
                "KeyType": "HASH",
            },
            {"AttributeName": "datacount", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "device_id",
                "AttributeType": "S",
            },
            {"AttributeName": "datacount", "AttributeType": "N"},
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10,
        },
    )
    data = [
        {
            "device_id": "10001",
            "datacount": 1,
            "info": {
                "info_timestamp": "1612519200",
                "temperature1": Decimal(str(37.2)),
                "temperature2": Decimal(str(21.31)),
                "temperature3": Decimal(str(25.6)),
                "temperature4": Decimal(str(22.96)),
                "temperature5": Decimal(str(24.69)),
            },
        },
        {
            "device_id": "10001",
            "datacount": 2,
            "info": {
                "info_timestamp": "1612521000",
                "temperature1": Decimal(str(24.34)),
                "temperature2": Decimal(str(24.59)),
                "temperature3": Decimal(str(19.2)),
                "temperature4": Decimal(str(29.11)),
                "temperature5": Decimal(str(23.18)),
            },
        },
        {
            "device_id": "10002",
            "datacount": 1,
            "info": {
                "info_timestamp": "1612519200",
                "temperature1": Decimal(str(14.34)),
                "temperature2": Decimal(str(17.59)),
                "temperature3": Decimal(str(11.2)),
                "temperature4": Decimal(str(15.95)),
                "temperature5": Decimal(str(16.17)),
            },
        },
        {
            "device_id": "10002",
            "datacount": 2,
            "info": {
                "info_timestamp": "1612521000",
                "temperature1": Decimal(str(13.04)),
                "temperature2": Decimal(str(15.01)),
                "temperature3": Decimal(str(18.91)),
                "temperature4": Decimal(str(16.45)),
                "temperature5": Decimal(str(16.21)),
            },
        },
        {
            "device_id": "10003",
            "datacount": 1,
            "info": {
                "info_timestamp": "1612519200",
                "temperature1": Decimal(str(34.23)),
                "temperature2": Decimal(str(36.21)),
                "temperature3": Decimal(str(31.24)),
                "temperature4": Decimal(str(32.02)),
                "temperature5": Decimal(str(29.54)),
            },
        },
        {
            "device_id": "10003",
            "datacount": 2,
            "info": {
                "info_timestamp": "1612521000",
                "temperature1": Decimal(str(34.55)),
                "temperature2": Decimal(str(33.13)),
                "temperature3": Decimal(str(32.62)),
                "temperature4": Decimal(str(39.32)),
                "temperature5": Decimal(str(38.87)),
            },
        },
    ]

    table = manager.service.Table("Devices")
    for device in data:

        table.put_item(Item=device)
    yield
    manager.client.delete_table(
        TableName="Devices",
    )
