# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
import json

from base_test import BaseTest
from client_builder import build_request, build_request_2
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets


REFRESHED_ACCESS_TOKEN = "refreshed-access-token-value"


class TestOAuthTokenRefresh(BaseTest):
    """Verify that the authenticator's refresh_token_updater causes
    CONTROL / CONNECTOR_CONFIG messages to be emitted so that
    rotated Microsoft refresh tokens are persisted back to config."""

    def _auth_client(self, http_mocker: HttpMocker) -> None:
        response = HttpResponse(
            json.dumps({"access_token": REFRESHED_ACCESS_TOKEN, "expires_in": 3600, "refresh_token": "rotated-refresh-token"}),
            200,
        )
        http_mocker.post(request=build_request(self._config), responses=response)
        http_mocker.post(request=build_request_2(self._config), responses=response)

    def _mock_accounts_read(self):
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="User/Query").with_body('{"UserId": null}').build(),
            HttpResponse(json.dumps(find_template("user_query", __file__)), 200),
        )
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search")
            .with_body(
                b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
            )
            .build(),
            HttpResponse(json.dumps(find_template("accounts_search", __file__)), 200),
        )

    def _read_accounts(self, config):
        catalog = CatalogBuilder().with_stream("accounts", SyncMode.full_refresh).build()
        return read_helper(config=config, catalog=catalog)

    def _written_back_config(self, output):
        control_messages = output.get_message_by_types([Type.CONTROL])
        assert len(control_messages) == 1
        return control_messages[0].control.connectorConfig.config

    def test_oauth_refresh_emits_control_message_with_updated_config(self):
        self._mock_accounts_read()
        output = self._read_accounts(self._config)

        control_messages = output.get_message_by_types([Type.CONTROL])
        assert (
            len(control_messages) > 0
        ), "Expected at least one CONTROL message with updated connector config (refresh_token_updater should persist rotated tokens)"
        ctrl = control_messages[0].control
        assert ctrl.type.value == "CONNECTOR_CONFIG"
        updated_config = ctrl.connectorConfig.config
        assert "refresh_token" in updated_config
        assert "access_token" in updated_config
        assert "token_expiry_date" in updated_config

    def test_written_back_access_token_is_masked_in_the_next_sync(self):
        self._mock_accounts_read()
        written_back_config = self._written_back_config(self._read_accounts(self._config))
        assert written_back_config["access_token"] == REFRESHED_ACCESS_TOKEN

        # The next sync starts from the written-back config with an unexpired token, so it does not refresh
        # and only the spec tells the secret filter that `access_token` is a secret.
        next_sync = self._read_accounts(written_back_config)

        assert not next_sync.errors
        assert len(next_sync.records) == len(find_template("accounts_search", __file__)["Accounts"])
        assert next_sync.get_message_by_types([Type.CONTROL]) == []
        assert filter_secrets(f"token={REFRESHED_ACCESS_TOKEN}") == "token=****"
