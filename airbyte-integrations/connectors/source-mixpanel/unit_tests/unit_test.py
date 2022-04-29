#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import logging
from datetime import date, timedelta

from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_mixpanel.source import Annotations
from source_mixpanel.source import SourceMixpanel

logger = logging.getLogger("test_client")

def test_check_connection_api_secret_ok(requests_mock):

    config = {"api_secret" : "testApiSecret"}

    service_account_headers = {
        "Authorization": "Basic api_secret:testApiSecret",
        "Accept": "application/json",
    }

    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/funnels/list", headers=service_account_headers)
    ok, error_msg = SourceMixpanel().check_connection(logger, config=config)

    assert ok
    assert not error_msg

def test_check_connection_service_account_ok(requests_mock):

    config = {
        "serviceaccount_username" : "testName",
        "serviceaccount_secret" : "testSecretName"
     }

    service_account_headers = {
        "Authorization": "Basic testName:testSecretName",
        "Accept": "application/json",
    }

    requests_mock.register_uri("GET", "https://mixpanel.com/api/2.0/funnels/list", headers=service_account_headers)
    ok, error_msg = SourceMixpanel().check_connection(logger, config=config)

    assert ok
    assert not error_msg

def test_check_connection_wrong_endpoint_not_ok(requests_mock):

    config = {}
    config["api_secret"] = "testApiSecret"

    service_account_headers = {
        "Authorization": "Basic api_secret:testApiSecret",
        "Accept": "application/json",
    }

    requests_mock.register_uri("GET", "NOT https://mixpanel.com/api/2.0/funnels/list", headers=service_account_headers)
    ok, error_msg = SourceMixpanel().check_connection(logger, config=config)

    assert not ok
    assert error_msg

def test_date_slices():

    now = date.today()
    # Test with start_date now range
    stream_slices = Annotations(authenticator=NoAuth(), start_date=now, end_date=now, date_window_size=1, region="EU").stream_slices(
        sync_mode="any"
    )
    assert 1 == len(stream_slices)

    stream_slices = Annotations(
        authenticator=NoAuth(), start_date=now - timedelta(days=1), end_date=now, date_window_size=1, region="US"
    ).stream_slices(sync_mode="any")
    assert 2 == len(stream_slices)

    stream_slices = Annotations(authenticator=NoAuth(), start_date=now - timedelta(days=2), end_date=now, date_window_size=1).stream_slices(
        sync_mode="any"
    )
    assert 3 == len(stream_slices)

    stream_slices = Annotations(
        authenticator=NoAuth(), start_date=now - timedelta(days=2), end_date=now, date_window_size=10
    ).stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    # test with attribution_window
    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=now - timedelta(days=2),
        end_date=now,
        date_window_size=1,
        attribution_window=5,
        region="US",
    ).stream_slices(sync_mode="any")
    assert 8 == len(stream_slices)

    # Test with start_date end_date range
    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=date.fromisoformat("2021-07-01"),
        end_date=date.fromisoformat("2021-07-01"),
        date_window_size=1,
        region="US",
    ).stream_slices(sync_mode="any")
    assert [{"start_date": "2021-07-01", "end_date": "2021-07-01"}] == stream_slices

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=date.fromisoformat("2021-07-01"),
        end_date=date.fromisoformat("2021-07-02"),
        date_window_size=1,
        region="EU",
    ).stream_slices(sync_mode="any")
    assert [{"start_date": "2021-07-01", "end_date": "2021-07-01"}, {"start_date": "2021-07-02", "end_date": "2021-07-02"}] == stream_slices

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=date.fromisoformat("2021-07-01"),
        end_date=date.fromisoformat("2021-07-03"),
        date_window_size=1,
        region="US",
    ).stream_slices(sync_mode="any")
    assert [
        {"start_date": "2021-07-01", "end_date": "2021-07-01"},
        {"start_date": "2021-07-02", "end_date": "2021-07-02"},
        {"start_date": "2021-07-03", "end_date": "2021-07-03"},
    ] == stream_slices

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=date.fromisoformat("2021-07-01"),
        end_date=date.fromisoformat("2021-07-03"),
        date_window_size=2,
        region="US",
    ).stream_slices(sync_mode="any")
    assert [{"start_date": "2021-07-01", "end_date": "2021-07-02"}, {"start_date": "2021-07-03", "end_date": "2021-07-03"}] == stream_slices

    # test with stream_state
    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=date.fromisoformat("2021-07-01"),
        end_date=date.fromisoformat("2021-07-03"),
        date_window_size=1,
    ).stream_slices(sync_mode="any", stream_state={"date": "2021-07-02"})
    assert [{"start_date": "2021-07-02", "end_date": "2021-07-02"}, {"start_date": "2021-07-03", "end_date": "2021-07-03"}] == stream_slices
