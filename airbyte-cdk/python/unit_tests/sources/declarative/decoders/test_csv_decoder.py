#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders import CsvDecoder


@pytest.mark.parametrize(
    "response_body, parameters, expected",
    [
        (
            "col1,col2\nval1,val2",
            {},
            [{"col1": "val1", "col2": "val2"}],
        ),
        (
            "col1;col2\nval1;val2",
            {"delimiter": ";"},
            [{"col1": "val1", "col2": "val2"}],
        ),
        (
            "malformed csv",
            {},
            [],  # Expect an empty dict on error
        ),
    ],
    ids=["with_header", "custom_delimiter", "malformed_csv"],
)
def test_csv_decoder(requests_mock, response_body, parameters, expected):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    results = list(CsvDecoder(parameters=parameters).decode(response))
    assert results == expected
