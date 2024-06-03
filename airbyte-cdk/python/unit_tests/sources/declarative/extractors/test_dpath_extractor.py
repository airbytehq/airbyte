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
    "field_path, body, expected_records",
    [
        (["data"], {"data": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        (["data"], {"data": {"id": 1}}, [{"id": 1}]),
        ([], {"id": 1}, [{"id": 1}]),
        ([], [{"id": 1}, {"id": 2}], [{"id": 1}, {"id": 2}]),
        (["data", "records"], {"data": {"records": [{"id": 1}, {"id": 2}]}}, [{"id": 1}, {"id": 2}]),
        (["{{ config['field'] }}"], {"record_array": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        (["{{ parameters['parameters_field'] }}"], {"record_array": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        (["record"], {"id": 1}, []),
        (["list", "*", "item"], {"list": [{"item": {"id": "1"}}]}, [{"id": "1"}]),
        (["data", "*", "list", "data2", "*"],
         {"data": [{"list": {"data2": [{"id": 1}, {"id": 2}]}}, {"list": {"data2": [{"id": 3}, {"id": 4}]}}]},
         [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]),
    ],
    ids=[
        "test_extract_from_array",
        "test_extract_single_record",
        "test_extract_single_record_from_root",
        "test_extract_from_root_array",
        "test_nested_field",
        "test_field_in_config",
        "test_field_in_parameters",
        "test_field_does_not_exist",
        "test_nested_list",
        "test_complex_nested_list",
    ]
)
def test_dpath_extractor(field_path, body, expected_records):
    extractor = DpathExtractor(field_path=field_path, config=config, decoder=decoder, parameters=parameters)

    response = create_response(body)
    actual_records = list(extractor.extract_records(response))

    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
