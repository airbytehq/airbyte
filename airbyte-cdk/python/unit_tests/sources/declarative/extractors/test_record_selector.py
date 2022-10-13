#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector


@pytest.mark.parametrize(
    "test_name, field_pointer, filter_template, body, expected_records",
    [
        (
            "test_with_extractor_and_filter",
            ["data"],
            "{{ record['created_at'] > stream_state['created_at'] }}",
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}]},
            [{"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
        ),
        (
            "test_no_record_filter_returns_all_records",
            ["data"],
            None,
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}]},
            [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}],
        ),
        (
            "test_with_extractor_and_filter_with_options",
            ["{{ options['options_field'] }}"],
            "{{ record['created_at'] > options['created_at'] }}",
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}]},
            [{"id": 3, "created_at": "06-08-21"}],
        ),
        (
            "test_read_single_record",
            ["data"],
            None,
            {"data": {"id": 1, "created_at": "06-06-21"}},
            [{"id": 1, "created_at": "06-06-21"}],
        ),
        (
            "test_no_record",
            ["data"],
            None,
            {"data": []},
            [],
        ),
        (
            "test_no_record_from_root",
            [],
            None,
            [],
            [],
        ),
    ],
)
def test_record_filter(test_name, field_pointer, filter_template, body, expected_records):
    config = {"response_override": "stop_if_you_see_me"}
    options = {"options_field": "data", "created_at": "06-07-21"}
    stream_state = {"created_at": "06-06-21"}
    stream_slice = {"last_seen": "06-10-21"}
    next_page_token = {"last_seen_id": 14}

    response = create_response(body)
    decoder = JsonDecoder(options={})
    extractor = DpathExtractor(field_pointer=field_pointer, decoder=decoder, config=config, options=options)
    if filter_template is None:
        record_filter = None
    else:
        record_filter = RecordFilter(config=config, condition=filter_template, options=options)
    record_selector = RecordSelector(extractor=extractor, record_filter=record_filter, options=options)

    actual_records = record_selector.select_records(
        response=response, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
    )
    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
