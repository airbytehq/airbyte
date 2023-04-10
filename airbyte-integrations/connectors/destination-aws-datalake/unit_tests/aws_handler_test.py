#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping

import pytest
from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import CompressionCodec, ConnectorConfig


@pytest.fixture(name="config")
def config() -> Mapping[str, Any]:
    with open("unit_tests/fixtures/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="config_prefix")
def config_prefix() -> Mapping[str, Any]:
    with open("unit_tests/fixtures/config_prefix.json", "r") as f:
        return json.loads(f.read())


def test_get_compression_type(config: Mapping[str, Any]):
    aws_handler = AwsHandler(ConnectorConfig(**config), DestinationAwsDatalake())

    tests = {
        CompressionCodec.GZIP: "gzip",
        CompressionCodec.SNAPPY: "snappy",
        CompressionCodec.ZSTD: "zstd",
        "LZO": None,
    }

    for codec, expected in tests.items():
        assert aws_handler._get_compression_type(codec) == expected


def test_get_path(config: Mapping[str, Any]):
    conf = ConnectorConfig(**config)
    aws_handler = AwsHandler(conf, DestinationAwsDatalake())

    tbl = "append_stream"
    db = conf.lakeformation_database_name
    assert aws_handler._get_s3_path(db, tbl) == "s3://datalake-bucket/test/append_stream/"


def test_get_path_prefix(config_prefix: Mapping[str, Any]):
    conf = ConnectorConfig(**config_prefix)
    aws_handler = AwsHandler(conf, DestinationAwsDatalake())

    tbl = "append_stream"
    db = conf.lakeformation_database_name
    assert aws_handler._get_s3_path(db, tbl) == "s3://datalake-bucket/prefix/test/append_stream/"
