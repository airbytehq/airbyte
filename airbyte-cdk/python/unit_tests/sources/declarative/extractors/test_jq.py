#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.jq import JqExtractor


@pytest.mark.parametrize(
    "test_name, body, transform_template, filter_template, expected_records",
    [
        ("test_extract_from_body_field", {"data": [{"id": 1}, {"id": 2}]}, ".data[]", None, [{"id": 1}, {"id": 2}]),
        ("test_extract_with_config_field", {"records": [{"id": 1}, {"id": 2}]}, ".{{ config['field'] }}[]", None, [{"id": 1}, {"id": 2}]),
        ("test_extract_with_kwargs", {"objects": [{"id": 1}, {"id": 2}]}, ".{{ kwargs['data_field'] }}[]", None, [{"id": 1}, {"id": 2}]),
        ("test_default", [{"id": 1}, {"id": 2}], ".{{kwargs['field']}}[]", None, [{"id": 1}, {"id": 2}]),
        (
            "test_using_state_filter",
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}]},
            ".data[]",
            "{{ record['created_at'] > stream_state['created_at'] }}",
            [{"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
        ),
        (
            "test_with_slice_filter",
            {"data": [{"id": 1, "last_seen": "06-06-21"}, {"id": 2, "last_seen": "06-07-21"}, {"id": 3, "last_seen": "06-10-21"}]},
            ".data[]",
            "{{ record['last_seen'] >= stream_slice['last_seen'] }}",
            [{"id": 3, "last_seen": "06-10-21"}],
        ),
        (
            "test_with_next_page_token_filter",
            {"data": [{"id": 11}, {"id": 12}, {"id": 13}, {"id": 14}, {"id": 15}]},
            ".data[]",
            "{{ record['id'] >= next_page_token['last_seen_id'] }}",
            [{"id": 14}, {"id": 15}],
        ),
        (
            "test_missing_filter_fields_return_no_results",
            {"data": [{"id": 11}, {"id": 12}, {"id": 13}, {"id": 14}, {"id": 15}]},
            ".data[]",
            "{{ record['id'] >= next_page_token['path_to_nowhere'] }}",
            [],
        ),
    ],
)
def test_jq(test_name, body, transform_template, filter_template, expected_records):
    config = {"field": "records"}
    kwargs = {"data_field": "objects"}
    stream_state = {"created_at": "06-06-21"}
    stream_slice = {"last_seen": "06-10-21"}
    next_page_token = {"last_seen_id": 14}
    decoder = JsonDecoder()

    response = create_response(body)

    extractor = JqExtractor(transform_template, decoder, config, filter_template, kwargs=kwargs)
    actual_records = extractor.extract_records(
        response=response, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
    )

    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
