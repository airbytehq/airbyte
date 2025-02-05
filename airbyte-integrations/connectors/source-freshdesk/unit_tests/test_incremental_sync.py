# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import pytest
from source_freshdesk.components import FreshdeskTicketsIncrementalSync

from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType


class TestFreshdeskTicketsIncrementalSync:
    @pytest.mark.parametrize(
        "stream_state, stream_slice, next_page_token, expected_params",
        [
            ({}, {"partition_field_start": "2022-01-01"}, {"next_page_token": 1}, {"partition_field_start": "2022-01-01"}),
            ({}, {"partition_field_start": "2021-01-01"}, {"next_page_token": "2022-01-01"}, {"partition_field_start": "2022-01-01"}),
        ],
    )
    def test_initialization_and_inheritance(self, mocker, stream_state, stream_slice, next_page_token, expected_params):
        sync = FreshdeskTicketsIncrementalSync("2022-01-01", "updated_at", "%Y-%m-%d", {}, {})

        # Setup mock for start_time_option.field_name.eval
        mock_field_name = mocker.MagicMock()
        mock_field_name.eval.return_value = "partition_field_start"

        mock_start_time_option_field_name = mocker.patch.object(sync, "start_time_option")
        mock_start_time_option_field_name.field_name = mock_field_name
        mock_start_time_option_field_name.inject_into = RequestOptionType("request_parameter")

        mock_partition_field_start = mocker.patch.object(sync, "_partition_field_start")
        mock_partition_field_start.eval.return_value = "partition_field_start"

        params = sync.get_request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        assert params == expected_params
