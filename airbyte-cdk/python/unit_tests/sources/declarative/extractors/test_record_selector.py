#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector


@pytest.mark.parametrize(
    "test_name, transform_template, filter_template, body, expected_records",
    [
        (
            "test_with_extractor_and_filter",
            "_.data",
            "{{ record['created_at'] > stream_state['created_at'] }}",
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}]},
            [{"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
        ),
        (
            "test_no_record_filter_returns_all_records",
            "_.data",
            None,
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}]},
            [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}],
        ),
    ],
)
def test_record_filter(test_name, transform_template, filter_template, body, expected_records):
    config = {"response_override": "stop_if_you_see_me"}
    stream_state = {"created_at": "06-06-21"}
    stream_slice = {"last_seen": "06-10-21"}
    next_page_token = {"last_seen_id": 14}

    response = create_response(body)
    decoder = JsonDecoder()
    extractor = JelloExtractor(transform=transform_template, decoder=decoder, config=config)
    if filter_template is None:
        record_filter = None
    else:
        record_filter = RecordFilter(config=config, condition=filter_template)
    record_selector = RecordSelector(extractor=extractor, record_filter=record_filter)

    actual_records = record_selector.select_records(
        response=response, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
    )
    assert actual_records == expected_records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
