#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor

config = {"field": "record_array"}
parameters = {"parameters_field": "record_array"}

decoder = JsonDecoder(parameters={})


@pytest.mark.parametrize(
    "test_name, field_path, body, expected_records",
    [
        ("test_extract_from_array", ["data"], {"data": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        ("test_extract_single_record", ["data"], {"data": {"id": 1}}, [{"id": 1}]),
        ("test_extract_single_record_from_root", [], {"id": 1}, [{"id": 1}]),
        ("test_extract_from_root_array", [], [{"id": 1}, {"id": 2}], [{"id": 1}, {"id": 2}]),
        ("test_nested_field", ["data", "records"], {"data": {"records": [{"id": 1}, {"id": 2}]}}, [{"id": 1}, {"id": 2}]),
        ("test_field_in_config", ["{{ config['field'] }}"], {"record_array": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        (
            "test_field_in_parameters",
            ["{{ parameters['parameters_field'] }}"],
            {"record_array": [{"id": 1}, {"id": 2}]},
            [{"id": 1}, {"id": 2}],
        ),
        ("test_field_does_not_exist", ["record"], {"id": 1}, []),
        ("test_nested_list", ["list", "*", "item"], {"list": [{"item": {"id": "1"}}]}, [{"id": "1"}]),
        (
            "test_complex_nested_list",
            ["data", "*", "list", "data2", "*"],
            {"data": [{"list": {"data2": [{"id": 1}, {"id": 2}]}}, {"list": {"data2": [{"id": 3}, {"id": 4}]}}]},
            [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
        ),
    ],
)
def test_dpath_extractor(test_name, field_path, body, expected_records):
    extractor = DpathExtractor(field_path=field_path, config=config, decoder=decoder, parameters=parameters)

    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
