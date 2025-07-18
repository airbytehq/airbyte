# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import unittest
from json import dumps, load
from typing import Dict

from components import IncrementalSingleBodyFilterCursor

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption


def config() -> Dict[str, str]:
    with open(
        "secrets/config.json",
    ) as f:
        yield load(f)


class TestGetRequestFilterOptions(unittest.TestCase):
    def setUp(self):
        self.instance = IncrementalSingleBodyFilterCursor(
            start_datetime=MinMaxDatetime(datetime="2024-03-25", datetime_format="%Y-%m-%dT%H:%M:%SZ", parameters=None),
            cursor_field="reviewTime",
            datetime_format="%Y-%m-%d",
            config=config,
            parameters=None,
        )

    def test_get_request_filter_options_no_stream_slice(self):
        expected = {}
        option_type = "body_json"
        result = self.instance._get_request_filter_options(option_type, None)
        assert result == expected

    def test_get_request_filter_options_with_start_time_option(self):
        expected = {"filter": {"reviewFromDate": "2024-03-25"}}

        self.instance.start_time_option = RequestOption(inject_into="body_json", field_name="filter, reviewFromDate", parameters=None)
        self.instance.stream_slice = {"start_time": "2024-03-25", "end_time": "2024-03-29"}
        option_type = "body_json"
        result = self.instance._get_request_filter_options(option_type, self.instance.stream_slice)
        assert result == expected


if __name__ == "__main__":
    unittest.main()
