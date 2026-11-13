#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import date
from unittest.mock import PropertyMock

import pytest
from freezegun import freeze_time
from source_outbrain_amplify.source import OutbrainAmplifyStream, SourceOutbrainAmplify

from airbyte_cdk.models import SyncMode


API_BASE_URL = "https://api.outbrain.com/amplify/v0.1/"


def _config(credentials=None):
    return {
        "credentials": credentials or {"type": "access_token", "access_token": "test-access-token"},
        "report_granularity": "daily",
        "geo_location_breakdown": "region",
        "start_date": "2022-04-01",
        "end_date": "2022-04-30",
    }


def _stream(source, config, name):
    return next(stream for stream in source.streams(config) if stream.name == name)


def test_marketers_request_uses_access_token_header(requests_mock, mocker):
    requests_mock.get(f"{API_BASE_URL}marketers/", json={"marketers": [{"id": "m1"}]})
    mocker.patch(
        "source_outbrain_amplify.source.Marketers.use_cache",
        new_callable=PropertyMock,
        return_value=False,
    )
    marketers = _stream(SourceOutbrainAmplify(), _config(), "marketers")

    records = list(marketers.read_records(sync_mode=SyncMode.full_refresh))

    assert records == [{"id": "m1"}]
    assert requests_mock.last_request.headers["OB-TOKEN-V1"] == "test-access-token"


def test_campaign_request_uses_access_token_header(requests_mock, mocker):
    requests_mock.get(f"{API_BASE_URL}marketers/", json={"marketers": [{"id": "m1"}]})
    requests_mock.get(f"{API_BASE_URL}marketers/m1/campaigns?limit=50", json={"campaigns": [{"id": "c1"}]})
    mocker.patch(
        "source_outbrain_amplify.source.Marketers.use_cache",
        new_callable=PropertyMock,
        return_value=False,
    )
    mocker.patch(
        "source_outbrain_amplify.source.CampaignsByMarketers.use_cache",
        new_callable=PropertyMock,
        return_value=False,
    )
    campaigns = _stream(SourceOutbrainAmplify(), _config(), "campaigns")

    records = []
    for stream_slice in campaigns.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(campaigns.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    assert records == [{"id": "c1"}]
    assert len(requests_mock.request_history) == 2
    assert all(request.headers["OB-TOKEN-V1"] == "test-access-token" for request in requests_mock.request_history)


def test_username_password_authenticates_once_for_marketers_request(requests_mock, mocker):
    config = _config({"type": "username_password", "username": "user", "password": "password"})
    requests_mock.get(f"{API_BASE_URL}login", json={"OB-TOKEN-V1": "tok"})
    requests_mock.get(f"{API_BASE_URL}marketers/", json={"marketers": [{"id": "m1"}]})
    mocker.patch(
        "source_outbrain_amplify.source.Marketers.use_cache",
        new_callable=PropertyMock,
        return_value=False,
    )
    marketers = _stream(SourceOutbrainAmplify(), config, "marketers")

    assert list(marketers.read_records(sync_mode=SyncMode.full_refresh)) == [{"id": "m1"}]

    assert requests_mock.call_count == 2
    assert requests_mock.request_history[0].url == f"{API_BASE_URL}login"
    assert requests_mock.request_history[1].headers["OB-TOKEN-V1"] == "tok"


def test_get_time_interval_parses_date_strings():
    start, end = OutbrainAmplifyStream._get_time_interval("2022-04-01", "2022-04-30")

    assert start.date() == date(2022, 4, 1)
    assert end.date() == date(2022, 4, 30)


@freeze_time("2022-04-30")
def test_get_time_interval_defaults_end_date_to_today():
    _, end = OutbrainAmplifyStream._get_time_interval("2022-04-01", None)

    assert end.date() == date(2022, 4, 30)


def test_get_time_interval_rejects_end_date_before_start_date():
    with pytest.raises(ValueError):
        OutbrainAmplifyStream._get_time_interval("2022-04-30", "2022-04-01")


def test_check_connection_with_valid_credentials(requests_mock):
    requests_mock.get(f"{API_BASE_URL}marketers/", json={"marketers": [{"id": "m1"}]})

    result = SourceOutbrainAmplify().check_connection(logging.getLogger(__name__), _config())

    assert result == (True, None)
