#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import PropertyMock
from urllib.parse import parse_qs, urlparse

from source_outbrain_amplify.source import SourceOutbrainAmplify

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


API_BASE_URL = "https://api.outbrain.com/amplify/v0.1/"
LEGACY_FULL_REFRESH_STATE = {"__ab_full_refresh_state_message": True}


def _config():
    return {
        "credentials": {"type": "access_token", "access_token": "test-access-token"},
        "report_granularity": "daily",
        "geo_location_breakdown": "region",
        "start_date": "2022-04-01",
        "end_date": "2022-04-30",
    }


def _read_stream(stream_name):
    config = _config()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    state = StateBuilder().with_stream_state(stream_name, LEGACY_FULL_REFRESH_STATE).build()
    return read(SourceOutbrainAmplify(), config=config, catalog=catalog, state=state)


def _assert_no_error_traces(output):
    assert output.errors == []
    assert all(message.trace.error is None for message in output.trace_messages)


def test_campaigns_substream_accepts_legacy_full_refresh_state(requests_mock, mocker):
    requests_mock.get(f"{API_BASE_URL}marketers/", json={"marketers": [{"id": "m1"}]})
    requests_mock.get(f"{API_BASE_URL}marketers/m1/campaigns?limit=50", json={"campaigns": [{"id": "c1"}]})
    mocker.patch("source_outbrain_amplify.source.Marketers.use_cache", new_callable=PropertyMock, return_value=False)
    mocker.patch("source_outbrain_amplify.source.CampaignsByMarketers.use_cache", new_callable=PropertyMock, return_value=False)

    output = _read_stream("campaigns")

    _assert_no_error_traces(output)
    assert [message.record.data for message in output.records] == [{"id": "c1"}]


def test_marketers_accepts_legacy_full_refresh_state_without_query_parameter(requests_mock, mocker):
    requests_mock.get(f"{API_BASE_URL}marketers/", json={"marketers": [{"id": "m1"}]})
    mocker.patch("source_outbrain_amplify.source.Marketers.use_cache", new_callable=PropertyMock, return_value=False)

    output = _read_stream("marketers")

    _assert_no_error_traces(output)
    stream = next(stream for stream in SourceOutbrainAmplify().streams(_config()) if stream.name == "marketers")
    assert stream.is_resumable is False
    assert [message.record.data for message in output.records] == [{"id": "m1"}]
    assert len(requests_mock.request_history) == 1
    assert "__ab_full_refresh_state_message" not in parse_qs(urlparse(requests_mock.last_request.url).query)


def test_parent_and_substream_are_not_resumable():
    streams = {stream.name: stream for stream in SourceOutbrainAmplify().streams(_config())}

    assert streams["marketers"].is_resumable is False
    assert streams["campaigns"].is_resumable is False
    assert streams["marketers"].get_cursor() is None
    assert streams["campaigns"].get_cursor() is None
