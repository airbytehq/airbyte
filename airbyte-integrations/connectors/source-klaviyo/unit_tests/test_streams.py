#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import urllib.parse
from datetime import datetime
from typing import Any, List, Mapping, Optional

import pendulum
import pytest
import requests
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from integration.config import KlaviyoConfigBuilder
from source_klaviyo.source import SourceKlaviyo

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_ANY_ATTEMPT_COUNT = 123
API_KEY = "some_key"
START_DATE = pendulum.datetime(2020, 10, 10)
CONFIG = {"api_key": API_KEY, "start_date": START_DATE}
CONFIG_NO_DATE = {"api_key": API_KEY}

EVENTS_STREAM_DEFAULT_START_DATE = "2012-01-01T00:00:00+00:00"
EVENTS_STREAM_CONFIG_START_DATE = "2021-11-08T00:00:00+00:00"
EVENTS_STREAM_STATE_DATE = (datetime.fromisoformat(EVENTS_STREAM_CONFIG_START_DATE) + relativedelta(years=1)).isoformat()
EVENTS_STREAM_TESTING_FREEZE_TIME = "2023-12-12 12:00:00"


def get_step_diff(provided_date: str) -> int:
    """
    This function returns the difference in weeks between provided date and freeze time.
    """
    provided_date = datetime.fromisoformat(provided_date).replace(tzinfo=None)
    freeze_date = datetime.strptime(EVENTS_STREAM_TESTING_FREEZE_TIME, "%Y-%m-%d %H:%M:%S")
    return (freeze_date - provided_date).days // 7


def read_records(stream_name: str, config: Mapping[str, Any], states: Mapping[str, Any] = dict()) -> List[Mapping[str, Any]]:
    state = StateBuilder()
    for stream_name_key in states:
        state.with_stream_state(stream_name_key, states[stream_name_key])
    source = SourceKlaviyo(CatalogBuilder().build(), config, state.build())
    output = read(
        source,
        config,
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name)).build(),
    )
    return [r.record.data for r in output.records]


def get_stream_by_name(stream_name: str, config: Mapping[str, Any], states: Mapping[str, Any] = dict()) -> Stream:
    state = StateBuilder()
    for stream_name_key in states:
        state.with_stream_state(stream_name_key, states[stream_name_key])
    source = SourceKlaviyo(CatalogBuilder().build(), KlaviyoConfigBuilder().build(), state.build())
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


class TestSemiIncrementalKlaviyoStream:
    @pytest.mark.parametrize(
        ("start_date", "stream_state", "input_records", "expected_records"),
        (
            (
                "2021-11-08T00:00:00Z",
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
                "2021-11-09T00:00:00Z",
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
            ("2021-11-08T00:00:00Z", "2022-11-07T00:00:00+00:00", [], []),
        ),
    )
    def test_read_records(self, start_date, stream_state, input_records, expected_records, requests_mock):
        state = {"metrics": {"updated": stream_state}} if stream_state else {}
        requests_mock.register_uri("GET", f"https://a.klaviyo.com/api/metrics", status_code=200, json={"data": input_records})
        records = read_records("metrics", CONFIG_NO_DATE | {"start_date": start_date}, state)
        assert records == expected_records


class TestProfilesStream:
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
                        "subscriptions": {"email": {"marketing": {"suppression": [{"reason": "SUPPRESSED"}]}}},
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
    @freeze_time(pendulum.datetime(2020, 11, 10).isoformat())
    def test_read_records(self, requests_mock):
        input_records = {
            "sms": {
                "true": {"attributes": {"name": "Some name 1", "archived": True, "updated_at": "2020-10-21T00:00:00+0000"}},
                "false": {"attributes": {"name": "Some name 1", "archived": False, "updated_at": "2020-10-20T00:00:00+0000"}},
            },
            "email": {
                "true": {"attributes": {"name": "Some name 1", "archived": True, "updated_at": "2020-10-18T00:00:00+0000"}},
                "false": {"attributes": {"name": "Some name 1", "archived": False, "updated_at": "2020-10-23T00:00:00+0000"}},
            },
        }

        stream = get_stream_by_name("campaigns", CONFIG)
        expected_records = [
            {
                "attributes": {"archived": True, "name": "Some name 1", "updated_at": "2020-10-21T00:00:00+0000", "channel": "sms"},
                "updated_at": "2020-10-21T00:00:00+0000",
            },
            {
                "attributes": {"archived": False, "name": "Some name 1", "updated_at": "2020-10-20T00:00:00+0000", "channel": "sms"},
                "updated_at": "2020-10-20T00:00:00+0000",
            },
            {
                "attributes": {"archived": True, "name": "Some name 1", "updated_at": "2020-10-18T00:00:00+0000", "channel": "email"},
                "updated_at": "2020-10-18T00:00:00+0000",
            },
            {
                "attributes": {"archived": False, "name": "Some name 1", "updated_at": "2020-10-23T00:00:00+0000", "channel": "email"},
                "updated_at": "2020-10-23T00:00:00+0000",
            },
        ]

        records = []
        base_url = "https://a.klaviyo.com/api/campaigns"

        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            query_params = {
                "filter": f"and(greater-or-equal(updated_at,{stream_slice['start_time']}),less-or-equal(updated_at,{stream_slice['end_time']}),equals(messages.channel,'{stream_slice['campaign_type']}'),equals(archived,{stream_slice['archived']}))",
                "sort": "updated_at",
            }
            encoded_query = urllib.parse.urlencode(query_params)
            encoded_url = f"{base_url}?{encoded_query}"
            requests_mock.register_uri(
                "GET",
                encoded_url,
                status_code=200,
                json={"data": input_records[stream_slice["campaign_type"]][stream_slice["archived"]]},
                complete_qs=True,
            )

            for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                records.append(record)

        assert len(records) == len(expected_records)
        for expected_record, record in zip(expected_records, records):
            assert expected_record == dict(record)
