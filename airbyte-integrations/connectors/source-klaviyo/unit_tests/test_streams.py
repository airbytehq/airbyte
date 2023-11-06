#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from pydantic import BaseModel
from source_klaviyo.availability_strategy import KlaviyoAvailabilityStrategy
from source_klaviyo.exceptions import KlaviyoBackoffError
from source_klaviyo.streams import (
    Campaigns,
    GlobalExclusions,
    IncrementalKlaviyoStream,
    KlaviyoStream,
    Profiles,
    SemiIncrementalKlaviyoStream,
)

API_KEY = "some_key"
START_DATE = pendulum.datetime(2020, 10, 10)


class SomeStream(KlaviyoStream):
    schema = mock.Mock(spec=BaseModel)
    max_time = 60 * 10

    def path(self, **kwargs) -> str:
        return "sub_path"


class SomeIncrementalStream(IncrementalKlaviyoStream):
    schema = mock.Mock(spec=BaseModel)
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "sub_path"


class SomeSemiIncrementalStream(SemiIncrementalKlaviyoStream):
    schema = mock.Mock(spec=BaseModel)
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "sub_path"


@pytest.fixture(name="response")
def response_fixture(mocker):
    return mocker.Mock(spec=requests.Response)


class TestKlaviyoStream:
    def test_request_headers(self):
        stream = SomeStream(api_key=API_KEY)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_headers = {
            "Accept": "application/json",
            "Revision": stream.api_revision,
            "Authorization": f"Klaviyo-API-Key {API_KEY}",
        }
        assert stream.request_headers(**inputs) == expected_headers

    @pytest.mark.parametrize(
        ("next_page_token", "page_size", "expected_params"),
        (
            ({"page[cursor]": "aaA0aAo0aAA0A"}, None, {"page[cursor]": "aaA0aAo0aAA0A"}),
            ({"page[cursor]": "aaA0aAo0aAA0A"}, 100, {"page[cursor]": "aaA0aAo0aAA0A"}),
            (None, None, {}),
            (None, 100, {"page[size]": 100}),
        ),
    )
    def test_request_params(self, next_page_token, page_size, expected_params):
        stream = SomeStream(api_key=API_KEY)
        stream.page_size = page_size
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": next_page_token}
        assert stream.request_params(**inputs) == expected_params

    @pytest.mark.parametrize(
        ("response_json", "next_page_token"),
        (
            (
                {
                    "data": [
                        {"type": "profile", "id": "00AA0A0AA0AA000AAAAAAA0AA0"},
                    ],
                    "links": {
                        "self": "https://a.klaviyo.com/api/profiles/",
                        "next": "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                        "prev": "null",
                    },
                },
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
            ),
            (
                {
                    "data": [
                        {"type": "profile", "id": "00AA0A0AA0AA000AAAAAAA0AA0"},
                    ],
                    "links": {
                        "self": "https://a.klaviyo.com/api/profiles/",
                        "prev": "null",
                    },
                },
                None,
            ),
        ),
    )
    def test_next_page_token(self, response, response_json, next_page_token):
        response.json.return_value = response_json
        stream = SomeStream(api_key=API_KEY)
        result = stream.next_page_token(response)

        assert result == next_page_token

    def test_availability_strategy(self):
        stream = SomeStream(api_key=API_KEY)
        assert isinstance(stream.availability_strategy, KlaviyoAvailabilityStrategy)

        expected_status_code = 401
        expected_message = (
            "This is most likely due to insufficient permissions on the credentials in use. "
            "Try to create and use an API key with read permission for the 'some_stream' stream granted"
        )
        reasons_for_unavailable_status_codes = stream.availability_strategy.reasons_for_unavailable_status_codes(stream, None, None, None)
        assert expected_status_code in reasons_for_unavailable_status_codes
        assert reasons_for_unavailable_status_codes[expected_status_code] == expected_message

    @pytest.mark.parametrize(
        ("status_code", "retry_after", "expected_time"),
        ((429, 30, 30.0), (429, None, None), (200, 30, None), (200, None, None)),
    )
    def test_backoff_time(self, status_code, retry_after, expected_time):
        stream = SomeStream(api_key=API_KEY)
        response_mock = mock.MagicMock()
        response_mock.status_code = status_code
        response_mock.headers = {"Retry-After": retry_after}
        assert stream.backoff_time(response_mock) == expected_time

    def test_backoff_time_large_retry_after(self):
        stream = SomeStream(api_key=API_KEY)
        response_mock = mock.MagicMock()
        response_mock.status_code = 429
        retry_after = stream.max_time + 5
        response_mock.headers = {"Retry-After": retry_after}
        with pytest.raises(KlaviyoBackoffError) as e:
            stream.backoff_time(response_mock)
        error_message = f"Stream some_stream has reached rate limit with 'Retry-After' of {float(retry_after)} seconds, exit from stream."
        assert str(e.value) == error_message


class TestIncrementalKlaviyoStream:
    def test_cursor_field_is_required(self):
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class IncrementalKlaviyoStream with abstract methods cursor_field, path"
        ):
            IncrementalKlaviyoStream(api_key=API_KEY, start_date=START_DATE.isoformat())

    @pytest.mark.parametrize(
        ("config_start_date", "stream_state_date", "next_page_token", "expected_params"),
        (
            (
                START_DATE.isoformat(),
                {"updated": "2023-01-01T00:00:00+00:00"},
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
                {
                    "filter": "greater-than(updated,2023-01-01T00:00:00+00:00)",
                    "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                    "sort": "updated",
                },
            ),
            (
                START_DATE.isoformat(),
                None,
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
                {
                    "filter": "greater-than(updated,2020-10-10T00:00:00+00:00)",
                    "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                    "sort": "updated",
                },
            ),
            (
                START_DATE.isoformat(),
                None,
                {"filter": "some_filter"},
                {"filter": "some_filter"},
            ),
            (
                None,
                None,
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
                {
                    "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                    "sort": "updated",
                },
            ),
            (
                None,
                {"updated": "2023-01-01T00:00:00+00:00"},
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
                {
                    "filter": "greater-than(updated,2023-01-01T00:00:00+00:00)",
                    "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                    "sort": "updated",
                },
            ),
        ),
    )
    def test_request_params(self, config_start_date, stream_state_date, next_page_token, expected_params):
        stream = SomeIncrementalStream(api_key=API_KEY, start_date=config_start_date)
        inputs = {"stream_state": stream_state_date, "next_page_token": next_page_token}
        assert stream.request_params(**inputs) == expected_params

    @pytest.mark.parametrize(
        ("config_start_date", "current_cursor", "latest_cursor", "expected_cursor"),
        (
            (START_DATE.isoformat(), "2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+00:00", "2023-01-02T00:00:00+00:00"),
            (START_DATE.isoformat(), "2023-01-02T00:00:00+00:00", "2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+00:00"),
            (START_DATE.isoformat(), None, "2019-01-01T00:00:00+00:00", "2020-10-10T00:00:00+00:00"),
            (None, "2020-10-10T00:00:00+00:00", "2019-01-01T00:00:00+00:00", "2020-10-10T00:00:00+00:00"),
            (None, None, "2019-01-01T00:00:00+00:00", "2019-01-01T00:00:00+00:00"),
        ),
    )
    def test_get_updated_state(self, config_start_date, current_cursor, latest_cursor, expected_cursor):
        stream = SomeIncrementalStream(api_key=API_KEY, start_date=config_start_date)
        inputs = {
            "current_stream_state": {stream.cursor_field: current_cursor} if current_cursor else {},
            "latest_record": {stream.cursor_field: latest_cursor},
        }
        assert stream.get_updated_state(**inputs) == {stream.cursor_field: expected_cursor}


class TestSemiIncrementalKlaviyoStream:
    def test_cursor_field_is_required(self):
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class SemiIncrementalKlaviyoStream with abstract methods cursor_field, path"
        ):
            SemiIncrementalKlaviyoStream(api_key=API_KEY, start_date=START_DATE.isoformat())

    @pytest.mark.parametrize(
        ("start_date", "stream_state", "input_records", "expected_records"),
        (
            (
                "2021-11-08T00:00:00",
                "2022-11-07T00:00:00",
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00"}},
                    {"attributes": {"updated": "2023-11-08T00:00:00"}},
                    {"attributes": {"updated": "2021-11-08T00:00:00"}},
                ],
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00"}, "updated": "2022-11-08T00:00:00"},
                    {"attributes": {"updated": "2023-11-08T00:00:00"}, "updated": "2023-11-08T00:00:00"},
                ],
            ),
            (
                "2021-11-08T00:00:00",
                None,
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00"}},
                    {"attributes": {"updated": "2023-11-08T00:00:00"}},
                    {"attributes": {"updated": "2021-11-08T00:00:00"}},
                ],
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00"}, "updated": "2022-11-08T00:00:00"},
                    {"attributes": {"updated": "2023-11-08T00:00:00"}, "updated": "2023-11-08T00:00:00"},
                ],
            ),
            (
                None,
                None,
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00"}},
                    {"attributes": {"updated": "2023-11-08T00:00:00"}},
                    {"attributes": {"updated": "2021-11-08T00:00:00"}},
                ],
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00"}, "updated": "2022-11-08T00:00:00"},
                    {"attributes": {"updated": "2023-11-08T00:00:00"}, "updated": "2023-11-08T00:00:00"},
                    {"attributes": {"updated": "2021-11-08T00:00:00"}, "updated": "2021-11-08T00:00:00"},
                ],
            ),
            (
                "2021-11-08T00:00:00",
                "2022-11-07T00:00:00",
                [],
                [],
            ),
        ),
    )
    def test_read_records(self, start_date, stream_state, input_records, expected_records, requests_mock):
        stream = SomeSemiIncrementalStream(api_key=API_KEY, start_date=start_date)
        requests_mock.register_uri("GET", f"https://a.klaviyo.com/api/{stream.path()}", status_code=200, json={"data": input_records})
        inputs = {
            "sync_mode": SyncMode.incremental,
            "cursor_field": stream.cursor_field,
            "stream_slice": None,
            "stream_state": {stream.cursor_field: stream_state} if stream_state else None,
        }
        assert list(stream.read_records(**inputs)) == expected_records


class TestProfilesStream:
    def test_parse_response(self, mocker):
        stream = Profiles(api_key=API_KEY, start_date=START_DATE.isoformat())
        json = {
            "data": [
                {
                    "type": "profile",
                    "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                    "attributes": {"email": "name@airbyte.io", "phone_number": "+11111111111", "updated": "2023-03-10T20:36:36+00:00"},
                    "properties": {"Status": "onboarding_complete"},
                },
                {
                    "type": "profile",
                    "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                    "attributes": {"email": "name2@airbyte.io", "phone_number": "+2222222222", "updated": "2023-02-10T20:36:36+00:00"},
                    "properties": {"Status": "onboarding_started"},
                },
            ],
            "links": {
                "self": "https://a.klaviyo.com/api/profiles/",
                "next": "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                "prev": "null",
            },
        }
        records = list(stream.parse_response(mocker.Mock(json=mocker.Mock(return_value=json))))
        assert records == [
            {
                "type": "profile",
                "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                "updated": "2023-03-10T20:36:36+00:00",
                "attributes": {"email": "name@airbyte.io", "phone_number": "+11111111111", "updated": "2023-03-10T20:36:36+00:00"},
                "properties": {"Status": "onboarding_complete"},
            },
            {
                "type": "profile",
                "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                "updated": "2023-02-10T20:36:36+00:00",
                "attributes": {"email": "name2@airbyte.io", "phone_number": "+2222222222", "updated": "2023-02-10T20:36:36+00:00"},
                "properties": {"Status": "onboarding_started"},
            },
        ]


class TestGlobalExclusionsStream:
    def test_parse_response(self, mocker):
        stream = GlobalExclusions(api_key=API_KEY, start_date=START_DATE.isoformat())
        json = {
            "data": [
                {
                    "type": "profile",
                    "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                    "attributes": {
                        "email": "name@airbyte.io",
                        "phone_number": "+11111111111",
                        "updated": "2023-03-10T20:36:36+00:00",
                        "subscriptions": {
                            "email": {"marketing": {"suppressions": [{"reason": "SUPPRESSED", "timestamp": "2021-05-18T01:29:51+00:00"}]}},
                        },
                    },
                },
                {
                    "type": "profile",
                    "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                    "attributes": {"email": "name2@airbyte.io", "phone_number": "+2222222222", "updated": "2023-02-10T20:36:36+00:00"},
                },
            ],
            "links": {
                "self": "https://a.klaviyo.com/api/profiles/",
                "next": "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                "prev": "null",
            },
        }
        records = list(stream.parse_response(mocker.Mock(json=mocker.Mock(return_value=json))))
        assert records == [
            {
                "type": "profile",
                "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                "attributes": {
                    "email": "name@airbyte.io",
                    "phone_number": "+11111111111",
                    "updated": "2023-03-10T20:36:36+00:00",
                    "subscriptions": {
                        "email": {"marketing": {"suppressions": [{"reason": "SUPPRESSED", "timestamp": "2021-05-18T01:29:51+00:00"}]}},
                    },
                },
                "updated": "2023-03-10T20:36:36+00:00",
            }
        ]


class TestCampaignsStream:
    def test_read_records(self, requests_mock):
        input_records = [
            {"attributes": {"name": "Some name 1", "archived": False, "updated_at": "2021-05-12T20:45:47+00:00"}},
            {"attributes": {"name": "Some name 2", "archived": False, "updated_at": "2021-05-12T20:45:47+00:00"}},
        ]
        input_records_archived = [
            {"attributes": {"name": "Archived", "archived": True, "updated_at": "2021-05-12T20:45:47+00:00"}},
        ]

        stream = Campaigns(api_key=API_KEY)
        requests_mock.register_uri(
            "GET", "https://a.klaviyo.com/api/campaigns?sort=updated_at", status_code=200, json={"data": input_records}, complete_qs=True
        )
        requests_mock.register_uri(
            "GET",
            "https://a.klaviyo.com/api/campaigns?sort=updated_at&filter=equals(archived,true)",
            status_code=200,
            json={"data": input_records_archived},
            complete_qs=True,
        )

        inputs = {"sync_mode": SyncMode.full_refresh, "cursor_field": stream.cursor_field, "stream_slice": None, "stream_state": None}
        expected_records = [
            {
                "attributes": {"name": "Some name 1", "archived": False, "updated_at": "2021-05-12T20:45:47+00:00"},
                "updated_at": "2021-05-12T20:45:47+00:00",
            },
            {
                "attributes": {"name": "Some name 2", "archived": False, "updated_at": "2021-05-12T20:45:47+00:00"},
                "updated_at": "2021-05-12T20:45:47+00:00",
            },
            {
                "attributes": {"name": "Archived", "archived": True, "updated_at": "2021-05-12T20:45:47+00:00"},
                "updated_at": "2021-05-12T20:45:47+00:00",
            },
        ]
        assert list(stream.read_records(**inputs)) == expected_records

    @pytest.mark.parametrize(
        ("latest_record", "current_stream_state", "expected_state"),
        (
            (
                {"attributes": {"archived": False, "updated_at": "2023-01-02T00:00:00+00:00"}, "updated_at": "2023-01-02T00:00:00+00:00"},
                {"updated_at": "2023-01-01T00:00:00+00:00", "archived": {"updated_at": "2023-01-01T00:00:00+00:00"}},
                {"updated_at": "2023-01-02T00:00:00+00:00", "archived": {"updated_at": "2023-01-01T00:00:00+00:00"}},
            ),
            (
                {"attributes": {"archived": False, "updated_at": "2023-01-02T00:00:00+00:00"}, "updated_at": "2023-01-02T00:00:00+00:00"},
                {"updated_at": "2023-01-01T00:00:00+00:00"},
                {"updated_at": "2023-01-02T00:00:00+00:00"},
            ),
            (
                {"attributes": {"archived": True, "updated_at": "2023-01-02T00:00:00+00:00"}, "updated_at": "2023-01-02T00:00:00+00:00"},
                {"updated_at": "2023-01-01T00:00:00+00:00", "archived": {"updated_at": "2023-01-01T00:00:00+00:00"}},
                {"updated_at": "2023-01-01T00:00:00+00:00", "archived": {"updated_at": "2023-01-02T00:00:00+00:00"}},
            ),
            (
                {"attributes": {"archived": True, "updated_at": "2023-01-02T00:00:00+00:00"}, "updated_at": "2023-01-02T00:00:00+00:00"},
                {"updated_at": "2023-01-01T00:00:00+00:00"},
                {"updated_at": "2023-01-01T00:00:00+00:00", "archived": {"updated_at": "2023-01-02T00:00:00+00:00"}},
            ),
            (
                {"attributes": {"archived": False, "updated_at": "2023-01-02T00:00:00+00:00"}, "updated_at": "2023-01-02T00:00:00+00:00"},
                {},
                {"updated_at": "2023-01-02T00:00:00+00:00"},
            ),
            (
                {"attributes": {"archived": True, "updated_at": "2023-01-02T00:00:00+00:00"}, "updated_at": "2023-01-02T00:00:00+00:00"},
                {},
                {"archived": {"updated_at": "2023-01-02T00:00:00+00:00"}},
            ),
        ),
    )
    def test_get_updated_state(self, latest_record, current_stream_state, expected_state):
        stream = Campaigns(api_key=API_KEY)
        assert stream.get_updated_state(current_stream_state, latest_record) == expected_state
