#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest import mock

import pendulum
import pytest
import requests
from pydantic import BaseModel
from source_klaviyo.streams import Events, IncrementalKlaviyoStream, KlaviyoStream, ReverseIncrementalKlaviyoStream

START_DATE = pendulum.datetime(2020, 10, 10)


class SomeStream(KlaviyoStream):
    schema = mock.Mock(spec=BaseModel)

    def path(self, **kwargs) -> str:
        return "sub_path"


class SomeIncrementalStream(IncrementalKlaviyoStream):
    schema = mock.Mock(spec=BaseModel)
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "sub_path"


class SomeReverseIncrementalStream(ReverseIncrementalKlaviyoStream):
    schema = mock.Mock(spec=BaseModel)
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "sub_path"


@pytest.fixture(name="response")
def response_fixture(mocker):
    return mocker.Mock(spec=requests.Response)


class TestKlaviyoStream:
    @pytest.mark.parametrize(
        ["response_json", "next_page_token"],
        [
            ({"end": 108, "total": 110, "page": 0}, {"page": 1}),  # first page
            ({"end": 108, "total": 110, "page": 9}, {"page": 10}),  # has next page
            ({"end": 109, "total": 110, "page": 9}, None),  # last page
        ],
    )
    def test_next_page_token(self, response, response_json, next_page_token):
        response.json.return_value = response_json
        stream = SomeStream(api_key="some_key")
        result = stream.next_page_token(response)

        assert result == next_page_token

    @pytest.mark.parametrize(
        ["next_page_token", "expected_params"],
        [
            ({"page": 10}, {"api_key": "some_key", "count": 100, "page": 10}),
            (None, {"api_key": "some_key", "count": 100}),
        ],
    )
    def test_request_params(self, next_page_token, expected_params):
        stream = SomeStream(api_key="some_key")
        result = stream.request_params(stream_state={}, next_page_token=next_page_token)

        assert result == expected_params

    def test_parse_response(self, response):
        response.json.return_value = {"data": [1, 2, 3, 4, 5]}
        stream = SomeStream(api_key="some_key")
        result = stream.parse_response(response)

        assert list(result) == response.json.return_value["data"]


class TestIncrementalKlaviyoStream:
    def test_cursor_field_is_required(self):
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class IncrementalKlaviyoStream with abstract methods cursor_field, path"
        ):
            IncrementalKlaviyoStream(api_key="some_key", start_date=START_DATE.isoformat())

    @pytest.mark.parametrize(
        ["next_page_token", "stream_state", "expected_params"],
        [
            # start with start_date
            (None, {}, {"api_key": "some_key", "count": 100, "sort": "asc", "since": START_DATE.int_timestamp}),
            # pagination overrule
            ({"since": 123}, {}, {"api_key": "some_key", "count": 100, "sort": "asc", "since": 123}),
            # start_date overrule state if state < start_date
            (
                None,
                {"updated_at": START_DATE.int_timestamp - 1},
                {"api_key": "some_key", "count": 100, "sort": "asc", "since": START_DATE.int_timestamp},
            ),
            # but pagination still overrule
            (
                {"since": 123},
                {"updated_at": START_DATE.int_timestamp - 1},
                {"api_key": "some_key", "count": 100, "sort": "asc", "since": 123},
            ),
            # and again
            (
                {"since": 123},
                {"updated_at": START_DATE.int_timestamp + 1},
                {"api_key": "some_key", "count": 100, "sort": "asc", "since": 123},
            ),
            # finally state > start_date and can be used
            (
                None,
                {"updated_at": START_DATE.int_timestamp + 1},
                {"api_key": "some_key", "count": 100, "sort": "asc", "since": START_DATE.int_timestamp + 1},
            ),
        ],
    )
    def test_request_params(self, next_page_token, stream_state, expected_params):
        stream = SomeIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        result = stream.request_params(stream_state=stream_state, next_page_token=next_page_token)

        assert result == expected_params

    @pytest.mark.parametrize(
        ["current_state", "latest_record", "expected_state"],
        [
            ({}, {"updated_at": 10, "some_field": 100}, {"updated_at": 10}),
            ({"updated_at": 11}, {"updated_at": 10, "some_field": 100}, {"updated_at": 11}),
            ({"updated_at": 11}, {"updated_at": 12, "some_field": 100}, {"updated_at": 12}),
            (
                {"updated_at": 12},
                {"updated_at": "2021-04-03 17:15:12", "some_field": 100},
                {"updated_at": datetime.strptime("2021-04-03 17:15:12", "%Y-%m-%d %H:%M:%S").timestamp()},
            ),
        ],
    )
    def test_get_updated_state(self, current_state, latest_record, expected_state):
        stream = SomeIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        result = stream.get_updated_state(current_stream_state=current_state, latest_record=latest_record)

        assert result == expected_state

    @pytest.mark.parametrize(
        ["response_json", "next_page_token"],
        [
            ({"next": 10, "total": 110, "page": 9}, {"since": 10}),  # has next page
            ({"total": 110, "page": 9}, None),  # last page
        ],
    )
    def test_next_page_token(self, response, response_json, next_page_token):
        response.json.return_value = response_json
        stream = SomeIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        result = stream.next_page_token(response)

        assert result == next_page_token


class TestReverseIncrementalKlaviyoStream:
    def test_cursor_field_is_required(self):
        with pytest.raises(
            TypeError,
            match="Can't instantiate abstract class ReverseIncrementalKlaviyoStream with abstract methods cursor_field, path",
        ):
            ReverseIncrementalKlaviyoStream(api_key="some_key", start_date=START_DATE.isoformat())

    def test_state_checkpoint_interval(self):
        stream = SomeReverseIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())

        assert stream.state_checkpoint_interval == stream.page_size, "reversed stream on the first read commit state for each page"

        stream.request_params(stream_state={"updated_at": START_DATE.isoformat()})
        assert stream.state_checkpoint_interval is None, "reversed stream should commit state only in the end"

    @pytest.mark.parametrize(
        ["next_page_token", "stream_state", "expected_params"],
        [
            (None, {}, {"api_key": "some_key", "count": 100, "sort": "asc"}),
            ({"page": 10}, {}, {"api_key": "some_key", "count": 100, "sort": "asc", "page": 10}),
            (None, {"updated_at": START_DATE.isoformat()}, {"api_key": "some_key", "count": 100, "sort": "desc"}),
            ({"page": 10}, {"updated_at": START_DATE.isoformat()}, {"api_key": "some_key", "count": 100, "sort": "desc", "page": 10}),
        ],
    )
    def test_request_params(self, next_page_token, stream_state, expected_params):
        stream = SomeReverseIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        result = stream.request_params(stream_state=stream_state, next_page_token=next_page_token)

        assert result == expected_params

    @pytest.mark.parametrize(
        ["current_state", "latest_record", "expected_state"],
        [
            ({}, {"updated_at": "2021-01-02T12:13:14", "some_field": 100}, {"updated_at": "2021-01-02T12:13:14+00:00"}),
            (
                {"updated_at": "2021-02-03T13:14:15"},
                {"updated_at": "2021-01-02T12:13:14", "some_field": 100},
                {"updated_at": "2021-02-03T13:14:15+00:00"},
            ),
            (
                {"updated_at": "2021-02-03T13:14:15"},
                {"updated_at": "2021-03-04T14:15:16", "some_field": 100},
                {"updated_at": "2021-03-04T14:15:16+00:00"},
            ),
        ],
    )
    def test_get_updated_state(self, current_state, latest_record, expected_state):
        stream = SomeReverseIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        result = stream.get_updated_state(current_stream_state=current_state, latest_record=latest_record)

        assert result == expected_state

    def test_next_page_token(self, response):
        ts_below_low_boundary = (START_DATE - pendulum.duration(hours=1)).isoformat()
        ts_above_low_boundary = (START_DATE + pendulum.duration(minutes=1)).isoformat()

        response.json.return_value = {
            "data": [{"updated_at": ts_below_low_boundary}, {"updated_at": ts_above_low_boundary}],
            "end": 108,
            "total": 110,
            "page": 9,
        }
        stream = SomeReverseIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        stream.request_params(stream_state={"updated_at": ts_below_low_boundary})
        next(iter(stream.parse_response(response)))

        result = stream.next_page_token(response)

        assert result is None

    def test_parse_response_read_backward(self, response):
        ts_state = START_DATE + pendulum.duration(minutes=30)
        ts_below_low_boundary = (ts_state - pendulum.duration(hours=1)).isoformat()
        ts_above_low_boundary = (ts_state + pendulum.duration(minutes=1)).isoformat()
        response.json.return_value = {
            "data": [{"updated_at": ts_above_low_boundary}, {"updated_at": ts_above_low_boundary}, {"updated_at": ts_below_low_boundary}],
            "end": 108,
            "total": 110,
            "page": 9,
        }
        stream = SomeReverseIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        stream.request_params(stream_state={"updated_at": ts_state.isoformat()})

        result = list(stream.parse_response(response))

        assert result == response.json.return_value["data"][:2], "should return all records until low boundary reached"

    def test_parse_response_read_forward(self, response):
        ts_below_low_boundary = (START_DATE - pendulum.duration(hours=1)).isoformat()
        ts_above_low_boundary = (START_DATE + pendulum.duration(minutes=1)).isoformat()

        response.json.return_value = {
            "data": [{"updated_at": ts_below_low_boundary}, {"updated_at": ts_below_low_boundary}, {"updated_at": ts_above_low_boundary}],
            "end": 108,
            "total": 110,
            "page": 9,
        }
        stream = SomeReverseIncrementalStream(api_key="some_key", start_date=START_DATE.isoformat())
        stream.request_params(stream_state={})

        result = list(stream.parse_response(response))

        assert result == response.json.return_value["data"][2:], "should all records younger then start_datetime"


class TestEventsStream:
    def test_parse_response(self, mocker):
        stream = Events(api_key="some_key", start_date=START_DATE.isoformat())
        json = {
            "data": [
                {"event_properties": {"$flow": "ordinary", "$message": "hello"}, "some_key": "some_value"},
                {"event_properties": {"$flow": "advanced", "$message": "nice to meet you"}, "another_key": "another_value"},
            ]
        }
        records = list(stream.parse_response(mocker.Mock(json=mocker.Mock(return_value=json))))
        assert records == [
            {
                "campaign_id": None,
                "event_properties": {"$flow": "ordinary", "$message": "hello"},
                "flow_id": "ordinary",
                "flow_message_id": "hello",
                "some_key": "some_value",
            },
            {
                "another_key": "another_value",
                "campaign_id": None,
                "event_properties": {"$flow": "advanced", "$message": "nice to meet you"},
                "flow_id": "advanced",
                "flow_message_id": "nice to meet you",
            },
        ]
