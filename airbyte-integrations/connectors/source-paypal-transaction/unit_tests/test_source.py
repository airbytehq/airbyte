#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_paypal_transaction.source import PayPalOauth2Authenticator, get_endpoint


class TestAuthentication:
    def test_init_token_authentication_init(self, authenticator_instance):
        assert isinstance(authenticator_instance, PayPalOauth2Authenticator)

    def test_get_refresh_request_body(self, authenticator_instance):
        expected_body = {"grant_type": "client_credentials"}
        assert authenticator_instance.get_refresh_request_body() == expected_body

    def test_oauth2_refresh_token_ok(self, requests_mock, authenticator_instance, api_endpoint):
        requests_mock.post(f"{api_endpoint}/v1/oauth2/token", json={"access_token": "test_access_token", "expires_in": 12345})
        result = authenticator_instance.refresh_access_token()
        assert result == ("test_access_token", 12345)

    def test_oauth2_refresh_token_failed(self, requests_mock, authenticator_instance, api_endpoint, error_while_refreshing_access_token):
        requests_mock.post(f"{api_endpoint}/v1/oauth2/token", json={})
        try:
            authenticator_instance.refresh_access_token()
        except Exception as e:
            assert e.args[0] == error_while_refreshing_access_token

    def test_new_oauth2_refresh_token_ok(self, requests_mock, new_format_authenticator_instance, api_endpoint):
        requests_mock.post(f"{api_endpoint}/v1/oauth2/token", json={"access_token": "test_access_token", "expires_in": 12345})
        result = new_format_authenticator_instance.refresh_access_token()
        assert result == ("test_access_token", 12345)

    def test_streams_count(self, prod_config, source_instance):
        assert len(source_instance.streams(prod_config)) == 2

    def test_check_connection_ok(self, requests_mock, prod_config, api_endpoint, transactions, source_instance):
        requests_mock.post(f"{api_endpoint}/v1/oauth2/token", json={"access_token": "test_access_token", "expires_in": 12345})
        url = (
            f"{api_endpoint}/v1/reporting/transactions"
            + "?start_date=2021-07-01T00%3A00%3A00%2B00%3A00&end_date=2021-07-02T00%3A00%3A00%2B00%3A00&fields=all&page_size=500&page=1"
        )
        requests_mock.get(url, json=transactions)
        assert source_instance.check_connection(logger=MagicMock(), config=prod_config) == (True, None)

    def test_check_connection_error(self, requests_mock, prod_config, api_endpoint, source_instance):
        requests_mock.post(f"{api_endpoint}/v1/oauth2/token", json={"access_token": "test_access_token", "expires_in": 12345})
        url = (
            f"{api_endpoint}/v1/reporting/transactions"
            + "?start_date=2021-07-01T00%3A00%3A00%2B00%3A00&end_date=2021-07-02T00%3A00%3A00%2B00%3A00&fields=all&page_size=500&page=1"
        )
        requests_mock.get(url, status_code=400, json={})
        assert not source_instance.check_connection(logger=MagicMock(), config=prod_config)[0]

    def test_get_prod_endpoint(self, prod_config, api_endpoint):
        assert get_endpoint(prod_config["is_sandbox"]) == api_endpoint

    def test_get_sandbox_endpoint(self, sandbox_config, sandbox_api_endpoint):
        assert get_endpoint(sandbox_config["is_sandbox"]) == sandbox_api_endpoint
