#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from source_pocket.extractor import PocketExtractor

options = {"options_field": "record_array"}
decoder = JsonDecoder(options={})


@pytest.mark.parametrize(
    "test_name, body, expected_records",
    [
        ("test_extract_successfully", {"list": {"record_one": {"id": 1}, "record_two": {"id": 2}}}, [{"id": 1}, {"id": 2}]),
        ("test_extract_empty_list", {"list": []}, []),
        ("test_field_pointer_does_not_exist", {"id": 1}, []),
    ],
)
def test_pocket_extractor(test_name, body, expected_records):
    extractor = PocketExtractor(decoder=decoder, options=options)

    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
