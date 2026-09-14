#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json

from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"

ACCOUNTS_JSON = {
    "accounts": [
        {
            "sid": "AC123",
            "date_created": "2022-01-01T00:00:00Z",
            "subresource_uris": {
                "usage": "/2010-04-01/Accounts/AC123/Usage.json",
            },
        }
    ],
}


class TestUsageRecords404Handling:
    """Test that usage_records stream handles 404 errors gracefully."""

    @HttpMocker()
    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_usage_records_ignores_404_responses(self, http_mocker: HttpMocker, caplog):
        """Test that the sync ignores 404 responses and logs the appropriate message."""
        http_mocker.get(
            HttpRequest(url=f"{BASE}/Accounts.json", query_params={"PageSize": "1000"}),
            HttpResponse(body=json.dumps(ACCOUNTS_JSON), status_code=200),
        )

        http_mocker.get(
            HttpRequest(
                url=f"{BASE}/Accounts/AC123/Usage/Records/Daily.json",
                query_params={"PageSize": "1000", "StartDate": "2022-11-15", "EndDate": "2022-11-16"},
            ),
            HttpResponse(
                body=json.dumps({"code": 20404, "message": "The requested resource was not found"}),
                status_code=404,
            ),
        )

        catalog = CatalogBuilder().with_stream("usage_records", SyncMode.full_refresh).build()
        config = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}

        output = read(get_source(config), config, catalog)

        assert len(output.records) == 0, "Expected no records when 404 is returned"

        expected_message = "Skipping this slice"
        log_messages = [record.message for record in caplog.records]
        assert any(
            expected_message in msg for msg in log_messages
        ), f"Expected log message containing '{expected_message}' not found in logs: {log_messages}"

    @HttpMocker()
    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_usage_records_completes_with_mixed_responses(self, http_mocker: HttpMocker):
        """Test that sync completes successfully with a sequence of 200, 404, 404, 200 responses."""
        accounts_json = {
            "accounts": [
                {"sid": "AC001", "date_created": "2022-01-01T00:00:00Z", "subresource_uris": {}},
                {"sid": "AC002", "date_created": "2022-01-02T00:00:00Z", "subresource_uris": {}},
                {"sid": "AC003", "date_created": "2022-01-03T00:00:00Z", "subresource_uris": {}},
                {"sid": "AC004", "date_created": "2022-01-04T00:00:00Z", "subresource_uris": {}},
            ],
        }
        http_mocker.get(
            HttpRequest(url=f"{BASE}/Accounts.json", query_params={"PageSize": "1000"}),
            HttpResponse(body=json.dumps(accounts_json), status_code=200),
        )

        http_mocker.get(
            HttpRequest(
                url=f"{BASE}/Accounts/AC001/Usage/Records/Daily.json",
                query_params={"PageSize": "1000", "StartDate": "2022-11-15", "EndDate": "2022-11-16"},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "usage_records": [
                            {
                                "account_sid": "AC001",
                                "category": "calls",
                                "start_date": "2022-11-15",
                                "end_date": "2022-11-16",
                                "count": "10",
                                "usage": "100",
                            }
                        ]
                    }
                ),
                status_code=200,
            ),
        )

        http_mocker.get(
            HttpRequest(
                url=f"{BASE}/Accounts/AC002/Usage/Records/Daily.json",
                query_params={"PageSize": "1000", "StartDate": "2022-11-15", "EndDate": "2022-11-16"},
            ),
            HttpResponse(
                body=json.dumps({"code": 20404, "message": "The requested resource was not found"}),
                status_code=404,
            ),
        )

        http_mocker.get(
            HttpRequest(
                url=f"{BASE}/Accounts/AC003/Usage/Records/Daily.json",
                query_params={"PageSize": "1000", "StartDate": "2022-11-15", "EndDate": "2022-11-16"},
            ),
            HttpResponse(
                body=json.dumps({"code": 20404, "message": "The requested resource was not found"}),
                status_code=404,
            ),
        )

        http_mocker.get(
            HttpRequest(
                url=f"{BASE}/Accounts/AC004/Usage/Records/Daily.json",
                query_params={"PageSize": "1000", "StartDate": "2022-11-15", "EndDate": "2022-11-16"},
            ),
            HttpResponse(
                body=json.dumps(
                    {
                        "usage_records": [
                            {
                                "account_sid": "AC004",
                                "category": "sms",
                                "start_date": "2022-11-15",
                                "end_date": "2022-11-16",
                                "count": "5",
                                "usage": "50",
                            }
                        ]
                    }
                ),
                status_code=200,
            ),
        )

        catalog = CatalogBuilder().with_stream("usage_records", SyncMode.full_refresh).build()
        config = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}

        output = read(get_source(config), config, catalog)

        assert len(output.records) == 2, f"Expected 2 records from successful responses, got {len(output.records)}"

        account_sids = [record.record.data["account_sid"] for record in output.records]
        assert "AC001" in account_sids, "Expected record from AC001"
        assert "AC004" in account_sids, "Expected record from AC004"

        assert output.errors == [], f"Expected no errors, but got: {output.errors}"

    @HttpMocker()
    @freeze_time("2022-11-16 12:03:11+00:00")
    def test_usage_records_incremental_with_404_handling(self, http_mocker: HttpMocker):
        """Test that incremental sync handles 404 responses correctly."""
        http_mocker.get(
            HttpRequest(url=f"{BASE}/Accounts.json", query_params={"PageSize": "1000"}),
            HttpResponse(body=json.dumps(ACCOUNTS_JSON), status_code=200),
        )

        http_mocker.get(
            HttpRequest(
                url=f"{BASE}/Accounts/AC123/Usage/Records/Daily.json",
                query_params={"PageSize": "1000", "StartDate": "2022-11-15", "EndDate": "2022-11-16"},
            ),
            HttpResponse(
                body=json.dumps({"code": 20404, "message": "The requested resource was not found"}),
                status_code=404,
            ),
        )

        catalog = CatalogBuilder().with_stream("usage_records", SyncMode.incremental).build()
        config = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}

        state = (
            StateBuilder()
            .with_stream_state(
                "usage_records", {"states": [{"partition": {"account_sid": "AC123"}, "cursor": {"start_date": "2022-11-13"}}]}
            )
            .build()
        )

        output = read(get_source(config, state), config, catalog, state)

        assert len(output.records) == 0, "Expected no records when 404 is returned in incremental sync"

        assert output.errors == [], f"Expected no errors, but got: {output.errors}"
