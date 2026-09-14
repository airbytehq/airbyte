#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import json

import requests
from components import NullCheckedDpathExtractor

from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder


def test_extractor_default_decoder_instantiates():
    extractor = NullCheckedDpathExtractor(
        field_path=["data"],
        nullable_nested_field="data",
        config={},
        parameters={},
    )
    assert isinstance(extractor.decoder, JsonDecoder)


def test_extract_records_returns_nested_data_or_parent():
    response = requests.Response()
    response._content = json.dumps(
        {
            "data": [
                {"item": "file", "id": 1, "data": {"id": 1, "name": "a"}},
                {"item": "file", "id": 2, "data": None},
            ]
        }
    ).encode()

    extractor = NullCheckedDpathExtractor(
        field_path=["data"],
        nullable_nested_field="data",
        config={},
        parameters={},
    )

    assert extractor.extract_records(response) == [
        {"id": 1, "name": "a"},
        {"item": "file", "id": 2, "data": None},
    ]
