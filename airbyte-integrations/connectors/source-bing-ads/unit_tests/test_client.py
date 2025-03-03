#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import socket
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch
from urllib.error import URLError

import pytest
import source_bing_ads.client
from bingads.authorization import AuthorizationData, OAuthTokens
from bingads.v13.bulk import BulkServiceManager
from bingads.v13.reporting.exceptions import ReportingDownloadException
from suds import sudsobject

from airbyte_cdk.utils import AirbyteTracedException


def test_sudsobject_todict_primitive_types():
    test_arr = ["1", "test", 1, [0, 0]]
    test_dict = {"k1": {"k2": 2, "k3": [1, 2, 3]}}
    test_date = datetime.utcnow()
    suds_obj = sudsobject.Object()
    suds_obj["int"] = 1
    suds_obj["arr"] = test_arr
    suds_obj["dict"] = test_dict
    suds_obj["date"] = test_date

    serialized_obj = source_bing_ads.client.Client.asdict(suds_obj)
    assert serialized_obj["int"] == 1
    assert serialized_obj["arr"] == test_arr
    assert serialized_obj["dict"] == test_dict
    assert serialized_obj["date"] == test_date.isoformat()


def test_sudsobject_todict_nested():
    test_date = datetime.utcnow()

    suds_obj = sudsobject.Object()
    nested_suds_1, nested_suds_2, nested_suds_3, nested_suds_4 = (
        sudsobject.Object(),
        sudsobject.Object(),
        sudsobject.Object(),
        sudsobject.Object(),
    )

    nested_suds_1["value"] = test_date
    nested_suds_2["value"] = 1
    nested_suds_3["value"] = "str"
    nested_suds_4["value"] = object()

    suds_obj["obj1"] = nested_suds_1
    suds_obj["arr"] = [nested_suds_2, nested_suds_3, nested_suds_4]

    serialized_obj = source_bing_ads.client.Client.asdict(suds_obj)
    assert serialized_obj["obj1"]["value"] == test_date.isoformat()
    assert serialized_obj["arr"][0]["value"] == nested_suds_2["value"]
    assert serialized_obj["arr"][1]["value"] == nested_suds_3["value"]
    assert serialized_obj["arr"][2]["value"] == nested_suds_4["value"]


def test_is_expired_true():
    def fake__init__(self, **kwargs):
        self.oauth = OAuthTokens(access_token_expires_in_seconds=10)
        self.oauth._access_token_received_datetime = datetime.utcnow() - timedelta(seconds=100)

    with mock.patch.object(source_bing_ads.client.Client, "__init__", fake__init__):
        client = source_bing_ads.client.Client()
        assert client.is_token_expiring() is True


def test_is_expired_true_with_delta_threshold():
    """
    Testing case when token still not expired actually, but refresh_token_safe_delta check is not passed
    """

    def fake__init__(self, **kwargs):
        expires_in = 100 + source_bing_ads.client.Client.refresh_token_safe_delta / 2
        self.oauth = OAuthTokens(access_token_expires_in_seconds=expires_in)
        self.oauth._access_token_received_datetime = datetime.utcnow() - timedelta(seconds=100)

    with mock.patch.object(source_bing_ads.client.Client, "__init__", fake__init__):
        client = source_bing_ads.client.Client()
        assert client.is_token_expiring() is True


def test_is_expired_false():
    def fake__init__(self, **kwargs):
        self.oauth = OAuthTokens(access_token_expires_in_seconds=100)
        self.oauth._access_token_received_datetime = datetime.utcnow() - timedelta(seconds=10)

    with mock.patch.object(source_bing_ads.client.Client, "__init__", fake__init__):
        client = source_bing_ads.client.Client()
        assert client.is_token_expiring() is False


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_get_auth_client(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    client._get_auth_client("client_id", "tenant_id")
    patched_request_tokens.assert_called_once_with("refresh_token")


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_get_auth_data(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    auth_data = client._get_auth_data()
    assert isinstance(auth_data, AuthorizationData)


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_handling_ReportingDownloadException(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    give_up = client.should_give_up(ReportingDownloadException(message="test"))
    assert False is give_up
    assert client._download_timeout == 310000
    client._download_timeout = 600000
    client.should_give_up(ReportingDownloadException(message="test"))
    assert client._download_timeout == 600000


def test_get_access_token(requests_mock):
    requests_mock.post(
        "https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token",
        status_code=400,
        json={
            "error": "invalid_grant",
            "error_description": "AADSTS70000: The user could not be authenticated as the grant is expired. The user must sign in again.",
        },
    )
    with pytest.raises(
        AirbyteTracedException,
        match="Failed to get OAuth access token by refresh token. The user could not be authenticated as the grant is expired. "
        "The user must sign in again.",
    ):
        source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")


def test_get_access_token_success(requests_mock):
    requests_mock.post(
        "https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token",
        status_code=200,
        json={"access_token": "test", "expires_in": "900", "refresh_token": "test"},
    )
    source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    assert requests_mock.call_count == 1


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_should_give_up(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    give_up = client.should_give_up(Exception())
    assert True is give_up
    give_up = client.should_give_up(URLError(reason="test"))
    assert True is give_up
    give_up = client.should_give_up(URLError(reason=socket.timeout()))
    assert False is give_up


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_get_service(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    service = client.get_service(service_name="CustomerManagementService")
    assert "customermanagement_service.xml" in service.service_url


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_get_reporting_service(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    service = client._get_reporting_service()
    assert (service._poll_interval_in_milliseconds, service._environment) == (client.report_poll_interval, client.environment)


@patch("bingads.authorization.OAuthWebAuthCodeGrant.request_oauth_tokens_by_refresh_token")
def test_bulk_service_manager(patched_request_tokens):
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    service = client._bulk_service_manager()
    assert (service._poll_interval_in_milliseconds, service._environment) == (5000, client.environment)


def test_get_bulk_entity(requests_mock):
    requests_mock.post(
        "https://login.microsoftonline.com/tenant_id/oauth2/v2.0/token",
        status_code=200,
        json={"access_token": "test", "expires_in": "9000", "refresh_token": "test"},
    )
    client = source_bing_ads.client.Client("tenant_id", "2020-01-01", client_id="client_id", refresh_token="refresh_token")
    with patch.object(BulkServiceManager, "download_file", return_value="file.csv"):
        bulk_entity = client.get_bulk_entity(data_scope=["EntityData"], download_entities=["AppInstallAds"])
        assert bulk_entity == "file.csv"
