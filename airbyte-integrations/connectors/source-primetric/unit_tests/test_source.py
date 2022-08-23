#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Mapping, Any
from unittest.mock import MagicMock
from source_primetric.source import SourcePrimetric
from airbyte_cdk.logger import AirbyteLogger
import json


def get_config() -> Mapping[str, Any]:
    filename = "secrets/config.json"
    with open(filename) as json_file:
        return json.load(json_file)


def test_check_connection(mocker):
    source = SourcePrimetric()
    logger_mock = MagicMock()
    config_mock = get_config()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourcePrimetric()
    config_mock = get_config()
    streams = source.streams(config_mock)
    expected_streams_number = 22
    assert len(streams) == expected_streams_number


def test_client_wrong_credentials():
    source = SourcePrimetric()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"client_id": "aaaaxxxxddddffff", "client_secret": "12341234"})
    assert not status
