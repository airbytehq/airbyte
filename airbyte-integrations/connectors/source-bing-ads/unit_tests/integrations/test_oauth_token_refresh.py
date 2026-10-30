# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
import json

from base_test import BaseTest
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestOAuthTokenRefresh(BaseTest):
    """Verify that the authenticator's refresh_token_updater causes
    CONTROL / CONNECTOR_CONFIG messages to be emitted so that
    rotated Microsoft refresh tokens are persisted back to config."""

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

    def test_oauth_refresh_emits_control_message_with_updated_config(self):
        self._mock_accounts_read()
        catalog = CatalogBuilder().with_stream("accounts", SyncMode.full_refresh).build()
        output = read_helper(config=self._config, catalog=catalog)

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
