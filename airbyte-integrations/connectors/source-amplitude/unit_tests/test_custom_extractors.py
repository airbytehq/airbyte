#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from unittest.mock import MagicMock

import pytest
import requests
from source_amplitude.components import ActiveUsersRecordExtractor, AverageSessionLengthRecordExtractor, EventsExtractor


@pytest.mark.parametrize(
    "custom_extractor, data, expected",
    [
        (
                ActiveUsersRecordExtractor,
                {
                    "xValues": ["2021-01-01", "2021-01-02"],
                    "series": [[1, 5]],
                    "seriesCollapsed": [[0]],
                    "seriesLabels": [0],
                    "seriesMeta": [{"segmentIndex": 0}],
                },
                [{"date": "2021-01-01", "statistics": {0: 1}}, {"date": "2021-01-02", "statistics": {0: 5}}],
        ),
        (
                ActiveUsersRecordExtractor,
                {
                    "xValues": ["2021-01-01", "2021-01-02"],
                    "series": [],
                    "seriesCollapsed": [[0]],
                    "seriesLabels": [0],
                    "seriesMeta": [{"segmentIndex": 0}],
                },
                [],
        ),
        (
                AverageSessionLengthRecordExtractor,
                {
                    "xValues": ["2019-05-23", "2019-05-24"],
                    "series": [[2, 6]],
                    "seriesCollapsed": [[0]],
                    "seriesLabels": [0],
                    "seriesMeta": [{"segmentIndex": 0}],
                },
                [{"date": "2019-05-23", "length": 2}, {"date": "2019-05-24", "length": 6}],
        ),
        (
                AverageSessionLengthRecordExtractor,
                {
                    "xValues": ["2019-05-23", "2019-05-24"],
                    "series": [],
                    "seriesCollapsed": [[0]],
                    "seriesLabels": [0],
                    "seriesMeta": [{"segmentIndex": 0}],
                },
                [],
        ),
    ],
    ids=["ActiveUsers", "EmptyActiveUsers", "AverageSessionLength", "EmptyAverageSessionLength"],
)
def test_parse_response(custom_extractor, data, expected):
    extractor = custom_extractor()
    response = requests.Response()
    response.json = MagicMock(return_value={'data': data})
    result = extractor.extract_records(response)
    assert result == expected


class TestEventsExtractor:
    extractor = EventsExtractor(config={}, parameters={'name': 'events'})

    def test_get_date_time_items_from_schema(self):
        expected = [
            "server_received_time",
            "event_time",
            "processed_time",
            "user_creation_time",
            "client_upload_time",
            "server_upload_time",
            "client_event_time",
        ]
        result = self.extractor._get_date_time_items_from_schema()
        assert result == expected

    @pytest.mark.parametrize(
        "record, expected",
        [
            ({}, {}),
            ({"event_time": "2021-05-27 11:59:53.710000"}, {"event_time": "2021-05-27T11:59:53.710000+00:00"}),
            ({"event_time": None}, {"event_time": None}),
            ({"event_time": ""}, {"event_time": ""}),
        ],
        ids=["empty_record", "transformed_record", "null_value", "empty_value"],
    )
    def test_date_time_to_rfc3339(self, record, expected):
        result = self.extractor._date_time_to_rfc3339(record)
        assert result == expected

    @pytest.mark.parametrize(
        "file_name, expected_records",
        [
            ('records.json.zip', [{"id": 123}]),
            ('zipped.json.gz', []),
        ],
        ids=["normal_file", "wrong_file"],
    )
    def test_parse_zip(self, requests_mock, file_name, expected_records):
        with open(f"{os.path.dirname(__file__)}/{file_name}", 'rb') as zipped:
            url = "https://amplitude.com/"
            requests_mock.get(url, content=zipped.read())
            response = requests.get(url)
            assert list(self.extractor.extract_records(response)) == expected_records
