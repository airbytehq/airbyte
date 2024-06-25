#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Optional
from unittest import mock

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel
from source_klaviyo.availability_strategy import KlaviyoAvailabilityStrategy
from source_klaviyo.exceptions import KlaviyoBackoffError
from source_klaviyo.source import SourceKlaviyo
from source_klaviyo.streams import Campaigns, CampaignsDetailed, IncrementalKlaviyoStream, KlaviyoStream

API_KEY = "some_key"
START_DATE = pendulum.datetime(2020, 10, 10)
CONFIG = {"api_key": API_KEY, "start_date": START_DATE}


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourceKlaviyo()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def get_records(stream: Stream, sync_mode: Optional[SyncMode] = SyncMode.full_refresh) -> List[Mapping[str, Any]]:
    records = []
    for stream_slice in stream.stream_slices(sync_mode=sync_mode):
        for record in stream.read_records(sync_mode=sync_mode, stream_slice=stream_slice):
            records.append(dict(record))
    return records


@pytest.fixture(name="response")
def response_fixture(mocker):
    return mocker.Mock(spec=requests.Response)


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


class TestKlaviyoStream:
    def test_request_headers(self):
        stream = SomeStream(api_key=API_KEY)
        expected_headers = {
            "Accept": "application/json", "Revision": stream.api_revision, "Authorization": f"Klaviyo-API-Key {API_KEY}"
        }
        assert stream.request_headers() == expected_headers

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
        assert stream.request_params(stream_state=None, next_page_token=next_page_token) == expected_params

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
                        "next": "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=aaA0aAo0aAA0AaAaAaa0AaaAAAaa",
                        "prev": "null",
                    },
                },
                {"page[cursor]": "aaA0aAo0aAA0AaAaAaa0AaaAAAaa"},
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
        reasons_for_unavailable_status_codes = stream.availability_strategy.reasons_for_unavailable_status_codes(
            stream, None, None, None
        )
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
        error_message = (
            f"Stream some_stream has reached rate limit with 'Retry-After' of {float(retry_after)} seconds, "
            "exit from stream."
        )
        assert str(e.value) == error_message


class TestIncrementalKlaviyoStream:
    def test_cursor_field_is_required(self):
        with pytest.raises(
            expected_exception=TypeError,
            match="Can't instantiate abstract class IncrementalKlaviyoStream with abstract methods cursor_field, path",
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
        assert stream.request_params(stream_state=stream_state_date, next_page_token=next_page_token) == expected_params

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
        assert stream._get_updated_state(
            current_stream_state={stream.cursor_field: current_cursor} if current_cursor else {},
            latest_record={stream.cursor_field: latest_cursor},
        ) == {stream.cursor_field: expected_cursor}


class TestSemiIncrementalKlaviyoStream:
    @pytest.mark.parametrize(
        ("start_date", "stream_state", "input_records", "expected_records"),
        (
            (
                "2021-11-08T00:00:00+00:00",
                "2022-11-07T00:00:00+00:00",
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00+00:00"}},
                    {"attributes": {"updated": "2023-11-08T00:00:00+00:00"}},
                    {"attributes": {"updated": "2021-11-08T00:00:00+00:00"}},
                ],
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00+00:00"}, "updated": "2022-11-08T00:00:00+00:00"},
                    {"attributes": {"updated": "2023-11-08T00:00:00+00:00"}, "updated": "2023-11-08T00:00:00+00:00"},
                ],
            ),
            (
                "2021-11-08T00:00:00+00:00",
                None,
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00+00:00"}},
                    {"attributes": {"updated": "2023-11-08T00:00:00+00:00"}},
                    {"attributes": {"updated": "2021-11-08T00:00:00+00:00"}},
                ],
                [
                    {"attributes": {"updated": "2022-11-08T00:00:00+00:00"}, "updated": "2022-11-08T00:00:00+00:00"},
                    {"attributes": {"updated": "2023-11-08T00:00:00+00:00"}, "updated": "2023-11-08T00:00:00+00:00"},
                ],
            ),
            ("2021-11-08T00:00:00+00:00", "2022-11-07T00:00:00+00:00", [], []),
        ),
    )
    def test_read_records(self, start_date, stream_state, input_records, expected_records, requests_mock):
        stream = get_stream_by_name("metrics", CONFIG | {"start_date": start_date})
        requests_mock.register_uri(
            "GET", f"https://a.klaviyo.com/api/metrics", status_code=200, json={"data": input_records}
        )
        stream.stream_state = {stream.cursor_field: stream_state if stream_state else start_date}
        records = get_records(stream=stream, sync_mode=SyncMode.incremental)
        assert records == expected_records


class TestProfilesStream:
    def test_request_params(self):
        stream = get_stream_by_name("profiles", CONFIG)
        assert stream.retriever.requester.get_request_params() == {"additional-fields[profile]": "predictive_analytics"}

    def test_read_records(self, requests_mock):
        stream = get_stream_by_name("profiles", CONFIG)
        json = {
            "data": [
                {
                    "type": "profile",
                    "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                    "attributes": {"email": "name@airbyte.io", "updated": "2023-03-10T20:36:36+00:00"},
                    "properties": {"Status": "onboarding_complete"},
                },
                {
                    "type": "profile",
                    "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                    "attributes": {"email": "name2@airbyte.io", "updated": "2023-02-10T20:36:36+00:00"},
                    "properties": {"Status": "onboarding_started"},
                },
            ],
        }
        requests_mock.register_uri("GET", f"https://a.klaviyo.com/api/profiles", status_code=200, json=json)

        records = get_records(stream=stream)
        assert records == [
            {
                "type": "profile",
                "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                "updated": "2023-03-10T20:36:36+00:00",
                "attributes": {"email": "name@airbyte.io", "updated": "2023-03-10T20:36:36+00:00"},
                "properties": {"Status": "onboarding_complete"},
            },
            {
                "type": "profile",
                "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                "updated": "2023-02-10T20:36:36+00:00",
                "attributes": {"email": "name2@airbyte.io", "updated": "2023-02-10T20:36:36+00:00"},
                "properties": {"Status": "onboarding_started"},
            },
        ]


class TestGlobalExclusionsStream:
    def test_read_records(self, requests_mock):
        stream = get_stream_by_name("global_exclusions", CONFIG)
        json = {
            "data": [
                {
                    "type": "profile",
                    "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                    "attributes": {
                        "updated": "2023-03-10T20:36:36+00:00",
                        "subscriptions": {"email": {"marketing": {"suppressions": [{"reason": "SUPPRESSED"}]}}},
                    },
                },
                {
                    "type": "profile",
                    "id": "AAAA1A1AA1AA111AAAAAAA1AA1",
                    "attributes": {"updated": "2023-02-10T20:36:36+00:00"},
                },
            ],
        }
        requests_mock.register_uri("GET", f"https://a.klaviyo.com/api/profiles", status_code=200, json=json)

        records = get_records(stream=stream)
        assert records == [
            {
                "type": "profile",
                "id": "00AA0A0AA0AA000AAAAAAA0AA0",
                "attributes": {
                    "updated": "2023-03-10T20:36:36+00:00",
                    "subscriptions": {"email": {"marketing": {"suppressions": [{"reason": "SUPPRESSED"}]}}},
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
            "GET",
            "https://a.klaviyo.com/api/campaigns?sort=updated_at",
            status_code=200,
            json={"data": input_records},
            complete_qs=True,
        )
        requests_mock.register_uri(
            "GET",
            "https://a.klaviyo.com/api/campaigns?sort=updated_at&filter=equals(archived,true)",
            status_code=200,
            json={"data": input_records_archived},
            complete_qs=True,
        )

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

        records = []
        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                records.append(record)

        assert records == expected_records

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
        assert stream._get_updated_state(current_stream_state, latest_record) == expected_state

    def test_stream_slices(self):
        stream = Campaigns(api_key=API_KEY)
        assert stream.stream_slices(sync_mode=SyncMode.full_refresh) == [{"archived": False}, {"archived": True}]

    @pytest.mark.parametrize(
        ("stream_state", "stream_slice", "next_page_token", "expected_params"),
        (
            ({}, {"archived": False}, None, {"sort": "updated_at"}),
            ({}, {"archived": True}, None, {"filter": "equals(archived,true)", "sort": "updated_at"}),
            (
                {"updated_at": "2023-10-10T00:00:00+00:00"},
                {"archived": False},
                None,
                {"filter": "greater-than(updated_at,2023-10-10T00:00:00+00:00)", "sort": "updated_at"},
            ),
            (
                {"archived": {"updated_at": "2023-10-10T00:00:00+00:00"}},
                {"archived": True},
                None,
                {
                    "filter": "and(greater-than(updated_at,2023-10-10T00:00:00+00:00),equals(archived,true))",
                    "sort": "updated_at",
                },
            ),
            (
                {"updated_at": "2023-10-10T00:00:00+00:00"},
                {"archived": False},
                {"page[cursor]": "next_page_cursor"},
                {
                    "filter": "greater-than(updated_at,2023-10-10T00:00:00+00:00)",
                    "sort": "updated_at",
                    "page[cursor]": "next_page_cursor",
                },
            ),
            (
                {"archived": {"updated_at": "2023-10-10T00:00:00+00:00"}},
                {"archived": True},
                {"page[cursor]": "next_page_cursor"},
                {
                    "filter": "and(greater-than(updated_at,2023-10-10T00:00:00+00:00),equals(archived,true))",
                    "sort": "updated_at",
                    "page[cursor]": "next_page_cursor",
                },
            ),
            (
                {},
                {"archived": True},
                {"page[cursor]": "next_page_cursor"},
                {"filter": "equals(archived,true)", "sort": "updated_at", "page[cursor]": "next_page_cursor"},
            ),
            (
                {},
                {"archived": False},
                {"page[cursor]": "next_page_cursor"},
                {"sort": "updated_at", "page[cursor]": "next_page_cursor"},
            ),
            (
                {"updated_at": "2023-10-10T00:00:00+00:00", "archived": {"updated_at": "2024-10-10T00:00:00+00:00"}},
                {"archived": False},
                None,
                {"filter": "greater-than(updated_at,2023-10-10T00:00:00+00:00)", "sort": "updated_at"},
            ),
            (
                {"updated_at": "2023-10-10T00:00:00+00:00", "archived": {"updated_at": "2022-10-10T00:00:00+00:00"}},
                {"archived": True},
                None,
                {
                    "filter": "and(greater-than(updated_at,2022-10-10T00:00:00+00:00),equals(archived,true))",
                    "sort": "updated_at",
                },
            ),
        ),
    )
    def test_request_params(self, stream_state, stream_slice, next_page_token, expected_params):
        stream = Campaigns(api_key=API_KEY)
        assert stream.request_params(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        ) == expected_params


class TestCampaignsDetailedStream:
    def test_set_recipient_count(self, requests_mock):
        stream = CampaignsDetailed(api_key=API_KEY)
        campaign_id = "1"
        record = {"id": campaign_id, "attributes": {"name": "Campaign"}}
        estimated_recipient_count = 5

        requests_mock.register_uri(
            "GET",
            f"https://a.klaviyo.com/api/campaign-recipient-estimations/{campaign_id}",
            status_code=200,
            json={"data": {"attributes": {"estimated_recipient_count": estimated_recipient_count}}},
        )
        stream._set_recipient_count(record)
        assert record["estimated_recipient_count"] == estimated_recipient_count

    def test_set_recipient_count_not_found(self, requests_mock):
        stream = CampaignsDetailed(api_key=API_KEY)
        campaign_id = "1"
        record = {"id": campaign_id, "attributes": {"name": "Campaign"}}

        requests_mock.register_uri(
            "GET",
            f"https://a.klaviyo.com/api/campaign-recipient-estimations/{campaign_id}",
            status_code=404,
            json={},
        )
        stream._set_recipient_count(record)
        assert record["estimated_recipient_count"] == 0

    def test_set_campaign_message(self, requests_mock):
        stream = CampaignsDetailed(api_key=API_KEY)
        message_id = "1"
        record = {"id": "123123", "attributes": {"name": "Campaign", "message": message_id}}
        campaign_message_data = {"type": "campaign-message", "id": message_id}

        requests_mock.register_uri(
            "GET",
            f"https://a.klaviyo.com/api/campaign-messages/{message_id}",
            status_code=200,
            json={"data": campaign_message_data},
        )
        stream._set_campaign_message(record)
        assert record["campaign_message"] == campaign_message_data

    def test_set_campaign_message_no_message_id(self):
        stream = CampaignsDetailed(api_key=API_KEY)
        record = {"id": "123123", "attributes": {"name": "Campaign"}}
        stream._set_campaign_message(record)
        assert "campaign_message" not in record
