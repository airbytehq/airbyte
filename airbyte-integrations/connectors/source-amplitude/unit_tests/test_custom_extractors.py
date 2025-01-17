#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import os
import re
import types
from contextlib import nullcontext as does_not_raise
from unittest.mock import MagicMock, patch

import pendulum
import pytest
import requests
from source_amplitude.components import ActiveUsersRecordExtractor, AverageSessionLengthRecordExtractor

from airbyte_cdk.utils import AirbyteTracedException


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
    response.json = MagicMock(return_value={"data": data})
    result = extractor.extract_records(response)
    assert result == expected


class TestEventsExtractor:
    extractor = EventsExtractor(config={}, parameters={"name": "events"})

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
            ("records.json.zip", [{"id": 123}]),
            ("zipped.json.gz", []),
        ],
        ids=["normal_file", "wrong_file"],
    )
    def test_parse_zip(self, requests_mock, file_name, expected_records):
        with open(f"{os.path.dirname(__file__)}/{file_name}", "rb") as zipped:
            url = "https://amplitude.com/"
            requests_mock.get(url, content=zipped.read())
            response = requests.get(url)
            assert list(self.extractor.extract_records(response)) == expected_records

    def test_event_read(self, requests_mock):
        stream = Events(
            authenticator=MagicMock(),
            start_date="2023-08-01T00:00:00Z",
            data_region="Standard Server",
            event_time_interval={"size_unit": "hours", "size": 24},
        )

        with open(f"{os.path.dirname(__file__)}/events_request_content.zip", "rb") as zipped:
            requests_mock.get("https://amplitude.com/api/2/export", content=zipped.read())

        records = stream.read_records(
            sync_mode=SyncMode.incremental, cursor_field="server_upload_time", stream_slice={"start": "20230701T00", "end": "20230701T23"}
        )

        assert len(list(records)) == 4

    @pytest.mark.parametrize(
        "error_code, expectation",
        [
            (400, pytest.raises(AirbyteTracedException)),
            (404, does_not_raise()),  # does not raise because response action is IGNORE
            (504, pytest.raises(AirbyteTracedException)),
            (500, does_not_raise()),  # does not raise because repsonse action is RETRY
        ],
    )
    def test_event_errors_read(self, mocker, requests_mock, error_code, expectation):
        stream = Events(
            authenticator=MagicMock(),
            start_date="2023-08-01T00:00:00Z",
            data_region="Standard Server",
            event_time_interval={"size_unit": "hours", "size": 24},
        )

        requests_mock.get("https://amplitude.com/api/2/export", status_code=error_code)

        mocker.patch("time.sleep", lambda x: None)

        with expectation:
            records = stream.read_records(
                sync_mode=SyncMode.incremental,
                cursor_field="server_upload_time",
                stream_slice={"start": "20230701T00", "end": "20230701T23"},
            )

            assert list(records) == []

    @pytest.mark.parametrize(
        "file_name, content_is_valid, records_count",
        [
            ("events_request_content.zip", True, 4),
            ("zipped.json.gz", False, 0),
        ],
    )
    def test_events_parse_response(self, file_name, content_is_valid, records_count):
        stream = Events(
            authenticator=MagicMock(),
            start_date="2023-08-01T00:00:00Z",
            data_region="Standard Server",
            event_time_interval={"size_unit": "hours", "size": 24},
        )

        with open(f"{os.path.dirname(__file__)}/{file_name}", "rb") as zipped:
            response = MagicMock()
            response.content = zipped.read()

        # Ensure `.parse_response()` returns a types.GeneratorType.
        # This was a main reason why the `Events` stream re-implemented as a separate python component
        assert isinstance(stream.parse_response(response, stream_state={}), types.GeneratorType)

        parsed_response = list(stream.parse_response(response, stream_state={}))

        assert len(parsed_response) == records_count

        if content_is_valid:
            # RFC3339 pattern
            pattern = r"^((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$"

            # Check datetime fields match RFC3339 pattern after `.parse_response()` being applied to records
            for record in parsed_response:
                assert re.match(pattern, record["server_received_time"]) is not None
                assert re.match(pattern, record["event_time"]) is not None
                assert re.match(pattern, record["processed_time"]) is not None
                assert re.match(pattern, record["client_upload_time"]) is not None
                assert re.match(pattern, record["server_upload_time"]) is not None
                assert re.match(pattern, record["client_event_time"]) is not None

    @pytest.mark.parametrize(
        "start_date, end_date, expected_slices",
        [
            (
                "2023-08-01T00:00:00Z",
                "2023-08-05T00:00:00Z",
                [
                    {"start": "20230801T00", "end": "20230801T23"},
                    {"start": "20230802T00", "end": "20230802T23"},
                    {"start": "20230803T00", "end": "20230803T23"},
                    {"start": "20230804T00", "end": "20230804T23"},
                    {"start": "20230805T00", "end": "20230805T23"},
                ],
            ),
            ("2023-08-05T00:00:00Z", "2023-08-01T00:00:00Z", []),
        ],
    )
    @patch("source_amplitude.streams.pendulum.now")
    def test_event_stream_slices(self, pendulum_now_mock, start_date, end_date, expected_slices):
        stream = Events(
            authenticator=MagicMock(),
            start_date=start_date,
            data_region="Standard Server",
            event_time_interval={"size_unit": "hours", "size": 24},
        )

        pendulum_now_mock.return_value = pendulum.parse(end_date)

        slices = stream.stream_slices(stream_state={})

        assert slices == expected_slices

    def test_event_request_params(self):
        stream = Events(
            authenticator=MagicMock(),
            start_date="2023-08-01T00:00:00Z",
            data_region="Standard Server",
            event_time_interval={"size_unit": "hours", "size": 24},
        )
        params = stream.request_params(stream_slice={"start": "20230801T00", "end": "20230801T23"})
        assert params == {"start": "20230801T00", "end": "20230801T23"}

    def test_updated_state(self):
        stream = Events(
            authenticator=MagicMock(),
            start_date="2023-08-01T00:00:00Z",
            data_region="Standard Server",
            event_time_interval={"size_unit": "hours", "size": 24},
        )

        # Sample is in unordered state on purpose. We need to ensure state allways keeps latest value
        cursor_fields_smaple = [
            {"server_upload_time": "2023-08-29"},
            {"server_upload_time": "2023-08-28"},
            {"server_upload_time": "2023-08-31"},
            {"server_upload_time": "2023-08-30"},
        ]

        state = {"server_upload_time": "2023-01-01"}
        for record in cursor_fields_smaple:
            state = stream._get_updated_state(state, record)

        assert state["server_upload_time"] == "2023-08-31 00:00:00.000000"
