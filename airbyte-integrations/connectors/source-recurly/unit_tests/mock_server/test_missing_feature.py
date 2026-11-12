# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .contracts import Parent, StreamCase, assert_requests, dated_params, given_parents, register
from .request_builder import RequestBuilder


CASES = [
    StreamCase("account_acquisitions", "acquisitions", dated_params(), {}),
    StreamCase("gift_cards", "gift_cards", {}, {}),
    StreamCase("external_subscriptions", "external_subscriptions", {"sort": "updated_at"}, {}),
    StreamCase(
        "external_subscription_payment_phases",
        "external_subscriptions/external1/external_payment_phases",
        {"sort": "updated_at", "order": "asc", "limit": "200"},
        {},
        parents=(Parent("external_subscriptions", {"sort": "updated_at"}, [{"id": "external1"}]),),
    ),
    StreamCase(
        "usage_records",
        "subscriptions/sub1/add_ons/addon1/usage",
        {"billing_status": "all", "sort": "usage_timestamp", "order": "asc", "limit": "200"},
        {},
        parents=(
            Parent(
                "subscriptions",
                {"sort": "updated_at", "order": "asc", "limit": "200"},
                [
                    {"id": "sub1", "add_ons": [{"subscription_id": "sub1", "add_on": {"id": "addon1"}}]},
                ],
            ),
        ),
    ),
    StreamCase("items", "items", dated_params(), {}),
    StreamCase("usage_records", "subscriptions", {"sort": "updated_at", "order": "asc", "limit": "200"}, {}),
    StreamCase("external_subscription_payment_phases", "external_subscriptions", {"sort": "updated_at"}, {}),
]


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=[
        "account_acquisitions",
        "gift_cards",
        "external_subscriptions",
        "external_subscription_payment_phases",
        "usage_records",
        "items",
        "subscription_add_ons_parent",
        "payment_phases_parent",
    ],
)
@pytest.mark.parametrize("error_type", ["missing_feature", "validation"])
def test_feature_errors(case: StreamCase, error_type: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(case.name, SyncMode.full_refresh).build()
    source = get_source(config, catalog=catalog)
    message = "This API operation is not enabled for this site" if error_type == "missing_feature" else "Invalid request parameters"
    with HttpMocker() as http_mocker:
        requests = []
        given_parents(http_mocker, requests, case)
        register(
            http_mocker,
            requests,
            RequestBuilder.endpoint(case.path).with_query_params(**case.params),
            HttpResponse(json.dumps({"error": {"type": error_type, "message": message}}), status_code=422),
        )
        output = read(source, config=config, catalog=catalog)
        assert not output.records
        if error_type == "missing_feature":
            assert not output.errors
            assert not any(log.log.level.value == "ERROR" for log in output.logs)
            assert any("Skipping feature-gated Recurly stream" in log.log.message and message in log.log.message for log in output.logs)
        else:
            assert output.errors
            assert any(message in log.log.message for log in output.logs if log.log.level.value == "ERROR")
        if error_type == "missing_feature":
            assert_requests(http_mocker, requests, len(case.parents) + 1)
        else:
            for request in requests[:-1]:
                http_mocker.assert_number_of_calls(request, 1)
            http_mocker.assert_number_of_calls(requests[-1], 6)
            assert http_mocker._mocker.call_count == len(case.parents) + 6
