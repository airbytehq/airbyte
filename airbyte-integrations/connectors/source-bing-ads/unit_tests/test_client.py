#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch

import source_bing_ads.client
from bingads.authorization import OAuthTokens
from suds import sudsobject


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
