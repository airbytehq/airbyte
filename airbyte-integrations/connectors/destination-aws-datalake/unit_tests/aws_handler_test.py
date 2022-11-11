#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping

from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import CompressionCodec, ConnectorConfig


def config_fixture() -> Mapping[str, Any]:
    with open("unit_tests/fixtures/config.json", "r") as f:
        return json.loads(f.read())


aws_handler = AwsHandler(ConnectorConfig(**config_fixture()), DestinationAwsDatalake())


def test_get_compression_type():
    tests = {
        CompressionCodec.GZIP: "gzip",
        CompressionCodec.SNAPPY: "snappy",
        CompressionCodec.ZSTD: "zstd",
        "LZO": None,
    }

    for codec, expected in tests.items():
        assert aws_handler._get_compression_type(codec) == expected
