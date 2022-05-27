#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.declarative.requesters.request_headers.interpolated_request_header_provider import (
    InterpolatedRequestHeaderProvider,
)


@pytest.mark.parametrize(
    "test_name, request_headers, expected_evaluated_headers",
    [
        ("test_static_string", {"static_key": "static_string"}, {"static_key": "static_string"}),
        ("test_static_number", {"static_key": 408}, {"static_key": 408}),
        ("test_from_config", {"get_from_config": "{{ config['config_key'] }}"}, {"get_from_config": "value_of_config"}),
        ("test_from_stream_state", {"get_from_state": "{{ stream_state['state_key'] }}"}, {"get_from_state": "state_value"}),
        ("test_from_stream_slice", {"get_from_slice": "{{ stream_slice['slice_key'] }}"}, {"get_from_slice": "slice_value"}),
        ("test_from_next_page_token", {"get_from_token": "{{ next_page_token['token_key'] }}"}, {"get_from_token": "token_value"}),
        ("test_from_stream_state_missing_key", {"get_from_state": "{{ stream_state['does_not_exist'] }}"}, {}),
        ("test_none_headers", None, {}),
    ],
)
def test_interpolated_request_header(test_name, request_headers, expected_evaluated_headers):
    config = {"config_key": "value_of_config"}
    stream_state = {"state_key": "state_value"}
    stream_slice = {"slice_key": "slice_value"}
    next_page_token = {"token_key": "token_value"}
    provider = InterpolatedRequestHeaderProvider(config=config, request_headers=request_headers)

    actual_headers = provider.request_headers(stream_state, stream_slice, next_page_token)
    assert actual_headers == expected_evaluated_headers
