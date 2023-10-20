#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock

import pendulum
import pytest
import requests
from pydantic import BaseModel
from source_klaviyo.availability_strategy import KlaviyoAvailabilityStrategyLatest
from source_klaviyo.streams import IncrementalKlaviyoStreamLatest, KlaviyoStreamLatest, Profiles

START_DATE = pendulum.datetime(2020, 10, 10)


class SomeStream(KlaviyoStreamLatest):
    schema = mock.Mock(spec=BaseModel)

    def path(self, **kwargs) -> str:
        return "sub_path"


class SomeIncrementalStream(IncrementalKlaviyoStreamLatest):
    schema = mock.Mock(spec=BaseModel)
    cursor_field = "updated"

    def path(self, **kwargs) -> str:
        return "sub_path"


@pytest.fixture(name="response")
def response_fixture(mocker):
    return mocker.Mock(spec=requests.Response)


class TestKlaviyoStreamLatest:
    api_key = "some_key"

    def test_request_headers(self):
        stream = SomeStream(api_key=self.api_key)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Revision": "2023-02-22",
            "Authorization": f"Klaviyo-API-Key {self.api_key}",
        }
        assert stream.request_headers(**inputs) == expected_headers

    @pytest.mark.parametrize(
        ("next_page_token", "expected_params"),
        (
            ({"page[cursor]": "aaA0aAo0aAA0A"}, {"page[cursor]": "aaA0aAo0aAA0A"}),
            (None, {"page[size]": 100}),  # 100 is a default page size defined in the class
        ),
    )
    def test_request_params(self, next_page_token, expected_params):
        stream = SomeStream(api_key=self.api_key)
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
        stream = SomeStream(api_key=self.api_key)
        result = stream.next_page_token(response)

        assert result == next_page_token

    def test_availability_strategy(self):
        stream = SomeStream(api_key=self.api_key)
        assert isinstance(stream.availability_strategy, KlaviyoAvailabilityStrategyLatest)

        expected_status_code = 401
        expected_message = (
            "This is most likely due to insufficient permissions on the credentials in use. "
            "Try to grant required permissions/scopes or re-authenticate"
        )
        reasons_for_unavailable_status_codes = stream.availability_strategy.reasons_for_unavailable_status_codes(stream, None, None, None)
        assert expected_status_code in reasons_for_unavailable_status_codes
        assert reasons_for_unavailable_status_codes[expected_status_code] == expected_message


class TestIncrementalKlaviyoStreamLatest:
    api_key = "some_key"
    start_date = START_DATE.isoformat()

    def test_cursor_field_is_required(self):
        with pytest.raises(
            TypeError, match="Can't instantiate abstract class IncrementalKlaviyoStreamLatest with abstract methods cursor_field, path"
        ):
            IncrementalKlaviyoStreamLatest(api_key=self.api_key, start_date=self.start_date)

    @pytest.mark.parametrize(
        ("stream_state_date", "next_page_token", "expected_params"),
        (
            (
                {"updated": "2023-01-01T00:00:00+00:00"},
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
                {
                    "filter": "greater-than(updated,2023-01-01T00:00:00+00:00)",
                    "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                    "sort": "updated",
                },
            ),
            (
                None,
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa"},
                {
                    "filter": "greater-than(updated,2020-10-10T00:00:00+00:00)",
                    "page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaaA00AAAa0AA00A0AAAaAa",
                    "sort": "updated",
                },
            ),
            (
                None,
                {"filter": "some_filter"},
                {"filter": "some_filter"},
            ),
        ),
    )
    def test_request_params(self, stream_state_date, next_page_token, expected_params):
        stream = SomeIncrementalStream(api_key=self.api_key, start_date=self.start_date)
        inputs = {"stream_state": stream_state_date, "next_page_token": next_page_token}
        assert stream.request_params(**inputs) == expected_params

    @pytest.mark.parametrize(
        ("current_cursor", "latest_cursor", "expected_cursor"),
        (
            ("2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+00:00", "2023-01-02T00:00:00+00:00"),
            ("2023-01-02T00:00:00+00:00", "2023-01-01T00:00:00+00:00", "2023-01-02T00:00:00+00:00"),
        ),
    )
    def test_get_updated_state(self, current_cursor, latest_cursor, expected_cursor):
        stream = SomeIncrementalStream(api_key=self.api_key, start_date=self.start_date)
        inputs = {
            "current_stream_state": {stream.cursor_field: current_cursor},
            "latest_record": {stream.cursor_field: latest_cursor},
        }
        assert stream.get_updated_state(**inputs) == {stream.cursor_field: expected_cursor}


class TestProfilesStream:
    def test_parse_response(self, mocker):
        stream = Profiles(api_key="some_key", start_date=START_DATE.isoformat())
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
