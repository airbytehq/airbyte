# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


API_KEY = "test-api-key"
CONFIG = {"api_key": API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
BASE_URL = "https://api.mention.net/api"
BEARER_HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def test_alert_read_sends_bearer_token_and_emits_alerts(http_mocker: HttpMocker) -> None:
    # Mention rejects a bare token with 401 invalid_token; only "Bearer <token>" is accepted.
    # Requests without the Bearer prefix do not match these mocks and fail the read.
    account_request = HttpRequest(url=f"{BASE_URL}/accounts/me", headers=BEARER_HEADERS)
    alerts_request = HttpRequest(url=f"{BASE_URL}/accounts/acc-1/alerts", query_params={"limit": "100"}, headers=BEARER_HEADERS)
    http_mocker.get(account_request, HttpResponse(json.dumps({"account": {"id": "acc-1", "name": "Acme"}}), 200))
    http_mocker.get(alerts_request, HttpResponse(json.dumps({"alerts": [{"id": 11, "name": "Brand"}, {"id": 12, "name": "Competitor"}], "_links": {}}), 200))

    catalog = CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build()
    output = read(get_source(CONFIG), CONFIG, catalog)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [11, 12]
    http_mocker.assert_number_of_calls(account_request, 1)
    http_mocker.assert_number_of_calls(alerts_request, 1)
