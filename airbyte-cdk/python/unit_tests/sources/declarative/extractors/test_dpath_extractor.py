#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor

config = {"field": "record_array"}
options = {"options_field": "record_array"}

decoder = JsonDecoder(options={})


@pytest.mark.parametrize(
    "test_name, field_pointer, body, expected_records",
    [
        ("test_extract_from_array", ["data"], {"data": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        ("test_extract_single_record", ["data"], {"data": {"id": 1}}, [{"id": 1}]),
        ("test_extract_from_root_array", [], [{"id": 1}, {"id": 2}], [{"id": 1}, {"id": 2}]),
        ("test_nested_field", ["data", "records"], {"data": {"records": [{"id": 1}, {"id": 2}]}}, [{"id": 1}, {"id": 2}]),
        ("test_field_in_config", ["{{ config['field'] }}"], {"record_array": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        ("test_field_in_options", ["{{ options['options_field'] }}"], {"record_array": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        ("test_field_does_not_exist", ["record"], {"id": 1}, []),
    ],
)
def test_dpath_extractor(test_name, field_pointer, body, expected_records):
    extractor = DpathExtractor(field_pointer=field_pointer, config=config, decoder=decoder, options=options)

    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
