#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor

config = {"field": "record_array"}

decoder = JsonDecoder()


@pytest.mark.parametrize(
    "test_name, transform, body, expected_records",
    [
        ("test_extract_from_array", "_.data", {"data": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        ("test_field_in_config", "_.{{ config['field'] }}", {"record_array": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}]),
        ("test_default", "_{{kwargs['field']}}", [{"id": 1}, {"id": 2}], [{"id": 1}, {"id": 2}]),
        (
            "test_remove_fields_from_records",
            "[{k:v for k,v in d.items() if k != 'value_to_remove'} for d in _.data]",
            {"data": [{"id": 1, "value": "HELLO", "value_to_remove": "fail"}, {"id": 2, "value": "WORLD", "value_to_remove": "fail"}]},
            [{"id": 1, "value": "HELLO"}, {"id": 2, "value": "WORLD"}],
        ),
        (
            "test_add_fields_from_records",
            "[{**{k:v for k,v in d.items()}, **{'project_id': d['project']['id']}} for d in _.data]",
            {"data": [{"id": 1, "value": "HELLO", "project": {"id": 8}}, {"id": 2, "value": "WORLD", "project": {"id": 9}}]},
            [
                {"id": 1, "value": "HELLO", "project_id": 8, "project": {"id": 8}},
                {"id": 2, "value": "WORLD", "project_id": 9, "project": {"id": 9}},
            ],
        ),
    ],
)
def test(test_name, transform, body, expected_records):
    extractor = JelloExtractor(transform, config, decoder)

    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
