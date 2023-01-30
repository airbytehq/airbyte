#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pendulum
import pytest
import requests
from source_amplitude.api import ActiveUsers, Annotations, AverageSessionLength, Cohorts, Events


class MockRequest:
    def __init__(self, status_code):
        self.status_code = status_code


class TestFullRefreshStreams:
    @pytest.mark.parametrize(
        "stream_cls, data, expected",
        [
            (Cohorts, [{"key": "value"}], [{"key": "value"}]),
            (Annotations, [{"key1": "value1"}], [{"key1": "value1"}]),
        ],
        ids=["Cohorts", "Annotations"],
    )
    def test_parse_response(self, requests_mock, stream_cls, data, expected):
        stream = stream_cls(data_region="Standard Server")
        url = f"{stream.url_base}{stream.path()}"
        data = {stream.data_field: data}
        requests_mock.get(url, json=data)
        response = requests.get(url)
        assert list(stream.parse_response(response)) == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Cohorts, None),
            (Annotations, None),
        ],
        ids=["Cohorts", "Annotations"],
    )
    def test_next_page_token(self, requests_mock, stream_cls, expected):
        stream = stream_cls(data_region="Standard Server")
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json={})
        response = requests.get(url)
        assert stream.next_page_token(response) == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Cohorts, "3/cohorts"),
            (Annotations, "2/annotations"),
        ],
        ids=["Cohorts", "Annotations"],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(data_region="Standard Server")
        assert stream.path() == expected


class TestIncrementalStreams:
    @pytest.mark.parametrize(
        "stream_cls, data, expected",
        [
            (
                ActiveUsers,
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
                ActiveUsers,
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
                AverageSessionLength,
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
                AverageSessionLength,
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
    def test_parse_response(self, requests_mock, stream_cls, data, expected):
        stream = stream_cls("2021-01-01T00:00:00Z", data_region="Standard Server")
        url = f"{stream.url_base}{stream.path()}"
        data = {stream.data_field: data}
        requests_mock.get(url, json=data)
        response = requests.get(url)
        result = list(stream.parse_response(response))
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (ActiveUsers, "2/users"),
            (AverageSessionLength, "2/sessions/average"),
            (Events, "2/export"),
        ],
        ids=["ActiveUsers", "AverageSessionLength", "Events"],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(pendulum.now().isoformat(), data_region="Standard Server")
        assert stream.path() == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (ActiveUsers, {"m": "active", "i": 1, "g": "country"}),
            (AverageSessionLength, {}),
        ],
        ids=["ActiveUsers", "AverageSessionLength"],
    )
    def test_request_params(self, stream_cls, expected):
        now = pendulum.now()
        stream = stream_cls(now.isoformat(), data_region="Standard Server")
        # update expected with valid start,end dates
        expected.update(**{"start": now.strftime(stream.date_template), "end": stream._get_end_date(now).strftime(stream.date_template)})
        assert stream.request_params({}) == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (ActiveUsers, {}),
            (AverageSessionLength, {}),
        ],
        ids=["ActiveUsers", "AverageSessionLength"],
    )
    def test_next_page_token(self, requests_mock, stream_cls, expected):
        days_ago = pendulum.now().subtract(days=2)
        stream = stream_cls(days_ago.isoformat(), data_region="Standard Server")
        start = days_ago.strftime(stream.date_template)
        end = pendulum.yesterday().strftime(stream.date_template)
        url = f"{stream.url_base}{stream.path()}?start={start}&end={end}"
        # update expected with test values.
        expected.update(
            **{"start": pendulum.yesterday().strftime(stream.date_template), "end": pendulum.now().strftime(stream.date_template)}
        )
        requests_mock.get(url)
        response = requests.get(url)
        assert stream.next_page_token(response) == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (ActiveUsers, ""),
            (AverageSessionLength, ""),
            (Events, ""),
        ],
        ids=["ActiveUsers", "AverageSessionLength", "Events"],
    )
    def test_get_end_date(self, stream_cls, expected):
        now = pendulum.now()
        yesterday = pendulum.yesterday()
        stream = stream_cls(yesterday.isoformat(), data_region="Standard Server")
        # update expected with test values.
        expected = now.strftime(stream.date_template)
        assert stream._get_end_date(yesterday).strftime(stream.date_template) == expected


class TestEventsStream:
    def test_parse_zip(self):
        stream = Events(pendulum.now().isoformat(), data_region="Standard Server")
        expected = [{"id": 123}]
        result = list(stream._parse_zip_file("unit_tests/api_data/zipped.json"))
        assert expected == result

    def test_stream_slices(self):
        stream = Events(pendulum.now().isoformat(), data_region="Standard Server")
        now = pendulum.now()
        expected = [
            {
                "start": now.strftime(stream.date_template),
                "end": stream._get_end_date(now).add(**stream.time_interval).subtract(hours=1).strftime(stream.date_template),
            }
        ]
        assert expected == stream.stream_slices()

    def test_request_params(self):
        stream = Events(pendulum.now().isoformat(), data_region="Standard Server")
        now = pendulum.now().subtract(hours=6)
        slice = {"start": now.strftime(stream.date_template), "end": stream._get_end_date(now).strftime(stream.date_template)}
        assert slice == stream.request_params(slice)

    def test_get_updated_state(self):
        stream = Events(pendulum.now().isoformat(), data_region="Standard Server")
        current_state = {"event_time": ""}
        latest_record = {"event_time": "2021-05-27 11:59:53.710000"}
        result = stream.get_updated_state(current_state, latest_record)
        assert result == latest_record

    def test_get_date_time_items_from_schema(self):
        stream = Events(pendulum.now().isoformat(), data_region="Standard Server")
        expected = [
            "server_received_time",
            "event_time",
            "processed_time",
            "user_creation_time",
            "client_upload_time",
            "server_upload_time",
            "client_event_time",
        ]
        result = stream._get_date_time_items_from_schema()
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
        stream = Events(pendulum.now().isoformat(), data_region="Standard Server")
        result = stream._date_time_to_rfc3339(record)
        assert result == expected
