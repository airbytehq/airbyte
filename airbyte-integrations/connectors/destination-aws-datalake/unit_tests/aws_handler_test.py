#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import pandas as pd
from destination_aws_datalake.config_reader import CompressionCodec

from typing import Any, Mapping

from destination_aws_datalake import DestinationAwsDatalake
from destination_aws_datalake.aws import AwsHandler
from destination_aws_datalake.config_reader import ConnectorConfig


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


def test_validate_athena_types():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["shoes", "tshirt", "ball"],
        "price": [50.3, 10.5, 20.0],
        "in_stock": [None, None, None]
    })

    aws_handler._validate_athena_types(df)
    assert df["in_stock"].dtype == 'O'
    assert df["price"].dtype == 'float64'
    assert df["name"].dtype == 'O'
    assert df["id"].dtype == 'int64'
