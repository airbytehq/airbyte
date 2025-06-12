# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
from typing import Any, Dict, Optional

from base_test import BaseTest
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class TestAccountsStream(BaseTest):
    stream_name = "accounts"

    def read_stream(
        self,
        stream_name: str,
        sync_mode: SyncMode,
        config: Dict[str, Any],
        stream_data_file: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        expecting_exception: bool = False,
    ) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
        return read_helper(
            config=config,
            catalog=catalog,
            state=state,
            expecting_exception=expecting_exception,
        )

    def test_read_accounts_tax_certificate_data(self):
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

        # Our account doesn't have configured Tax certificate.
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config)
        assert output.records[0].record.data["TaxCertificate"] == {
            "Status": "Active",
            "TaxCertificateBlobContainerName": "Test Container Name",
            "TaxCertificates": [{"key": "test_key", "value": "test_value"}],
        }

    def test_read_linked_agencies_data(self):
        """
        Test reading linked agencies data from the accounts stream.
        We are manually putting the data in CustomerInfo field through a transformation
        to keep it backward compatible with the SOAP response.
        """
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
            HttpResponse(json.dumps(find_template("accounts_search_with_linked_agencies", __file__)), 200),
        )

        # Our account doesn't have configured Tax certificate.
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config)
        assert output.records[0].record.data["LinkedAgencies"] == {
            "CustomerInfo": [
                {
                    "Id": 123456789,
                    "Name": "Ramp (MCC)",
                }
            ]
        }

    def test_read_accounts_with_account_names_predicate(self):
        """
        Test reading accounts data with account_names predicate in the config.
        This tests the ListPartitionRouter that processes the account_names configuration.
        """
        # Use a config with account_names predicate
        config_with_account_names = {
            **self._config,
            "account_names": [{"operator": "Equals", "name": "Airbyte"}, {"operator": "Contains", "name": "demo"}],
        }

        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="User/Query").with_body('{"UserId": null}').build(),
            HttpResponse(json.dumps(find_template("user_query", __file__)), 200),
        )

        # Mock the first Accounts/Search request with Equals operator for "Airbyte"
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search")
            .with_body(
                b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}, {"Field": "AccountName", "Operator": "Equals", "Value": "Airbyte"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
            )
            .build(),
            HttpResponse(json.dumps(find_template("accounts_search_equals_airbyte", __file__)), 200),
        )

        # Mock the second Accounts/Search request with Contains operator for "demo"
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search")
            .with_body(
                b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}, {"Field": "AccountName", "Operator": "Contains", "Value": "demo"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
            )
            .build(),
            HttpResponse(json.dumps(find_template("accounts_search_contains_demo", __file__)), 200),
        )

        # Read the accounts stream with account_names predicate
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, config_with_account_names)
        assert len(output.records) == 2
        account_names = [record.record.data["Name"] for record in output.records]
        assert "Airbyte" in account_names
        assert any("demo" in name.lower() for name in account_names)

    def test_read_accounts_with_account_names_predicate_that_returns_duplicated_records(self):
        """
        Test reading accounts data with account_names predicate in the config.
        In this scenario two predicates cause to get the same record twice and we need to filter.
        """
        # Use a config with account_names predicate
        config_with_account_names = {
            **self._config,
            "account_names": [
                {"operator": "Equals", "name": "Airbyte"},
                {"operator": "Contains", "name": "demo"},
                {"operator": "Contains", "name": "account"},
            ],
        }

        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="User/Query").with_body('{"UserId": null}').build(),
            HttpResponse(json.dumps(find_template("user_query", __file__)), 200),
        )

        # Mock the first Accounts/Search request with Equals operator for "Airbyte"
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search")
            .with_body(
                b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}, {"Field": "AccountName", "Operator": "Equals", "Value": "Airbyte"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
            )
            .build(),
            HttpResponse(json.dumps(find_template("accounts_search_equals_airbyte", __file__)), 200),
        )

        # Mock the second Accounts/Search request with Contains operator for "demo"
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search")
            .with_body(
                b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}, {"Field": "AccountName", "Operator": "Contains", "Value": "demo"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
            )
            .build(),
            HttpResponse(json.dumps(find_template("accounts_search_contains_demo", __file__)), 200),
        )

        # Mock the second Accounts/Search request with Contains operator for "account"
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search")
            .with_body(
                b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}, {"Field": "AccountName", "Operator": "Contains", "Value": "account"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
            )
            .build(),
            #  We return same response as the above mock to simulate the same record being returned twice.
            HttpResponse(json.dumps(find_template("accounts_search_contains_demo", __file__)), 200),
        )

        # Read the accounts stream with account_names predicate
        output = self.read_stream(self.stream_name, SyncMode.full_refresh, config_with_account_names)
        assert len(output.records) == 2
        account_names = [record.record.data["Name"] for record in output.records]
        assert "Airbyte" in account_names
        assert any("demo" in name.lower() for name in account_names)
        assert any("account" in name.lower() for name in account_names)
