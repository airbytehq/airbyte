# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@freeze_time("2025-01-02T00:00:00Z")
@pytest.mark.parametrize("grouping_key", [None, "region"])
@pytest.mark.parametrize("plan_id", [None, "plan-1"])
@pytest.mark.parametrize("empty_usage", [False, True])
def test_subscription_usage_read(get_source, grouping_key, plan_id, empty_usage) -> None:
    config = {"api_key": "test-token", "start_date": "2025-01-01T00:00:00Z", "end_date": "2025-01-02T00:00:00Z"}
    if grouping_key:
        config["subscription_usage_grouping_key"] = grouping_key
    if plan_id:
        config["plan_id"] = plan_id
    subscriptions = [
        {
            "id": f"sub-{index}",
            "plan": {"id": f"plan-{index}"},
            "customer": {"id": f"customer-{index}", "external_customer_id": f"external-{index}"},
            "created_at": "2025-01-01T12:00:00Z",
        }
        for index in (1, 2)
    ]
    parent_params = {"limit": "50", "created_at[gte]": "2025-01-01T00:00:00+00:00", "created_at[lte]": "2025-01-02T00:00:00+00:00"}
    expected = []
    requests = []
    with HttpMocker() as mocker:
        subscriptions_request = HttpRequest("https://api.billwithorb.com/v1/subscriptions", query_params=parent_params)
        requests.append(subscriptions_request)
        mocker.get(
            subscriptions_request,
            HttpResponse(json.dumps({"data": subscriptions})),
        )
        if grouping_key:
            plans = [
                {"id": f"plan-{index}", "prices": [{"billable_metric": {"id": f"metric-{index}-{metric}"}} for metric in (1, 2)]}
                for index in (1, 2)
            ]
            plans_request = HttpRequest("https://api.billwithorb.com/v1/plans", query_params=parent_params)
            requests.append(plans_request)
            mocker.get(
                plans_request,
                HttpResponse(json.dumps({"data": plans})),
            )
        for index in (1, 2):
            if plan_id and plan_id != f"plan-{index}":
                continue
            for metric in (1, 2) if grouping_key else (None,):
                params = {
                    "granularity": "day",
                    "timeframe_start": "2025-01-01T00:00:00.000000+0000",
                    "timeframe_end": "2025-01-02T00:00:00.000000+0000",
                }
                if grouping_key:
                    params.update(group_by=grouping_key, billable_metric_id=f"metric-{index}-{metric}")
                record = {
                    "id": f"usage-{index}-{metric}",
                    "billable_metric": {"id": f"metric-{index}-{metric}", "name": "API calls"},
                    "usage": [{"quantity": 5, "timeframe_start": "2025-01-01T00:00:00.000000+0000"}],
                }
                if grouping_key:
                    record["metric_group"] = {"property_key": "region", "property_value": "west"}
                usage_request = HttpRequest(f"https://api.billwithorb.com/v1/subscriptions/sub-{index}/usage", query_params=params)
                requests.append(usage_request)
                mocker.get(usage_request, HttpResponse(json.dumps({"data": [] if empty_usage else [record]})))
                if not empty_usage:
                    expected.append({key: value for key, value in record.items() if key != "usage"} | {"grouping_key": grouping_key or ""})
        catalog = CatalogBuilder().with_stream("subscription_usage", SyncMode.full_refresh).build()
        output = read(get_source(config, catalog), config, catalog)
        assert sorted([message.record.data for message in output.records], key=lambda record: record["id"]) == expected
        assert not output.errors
        for request in requests:
            mocker.assert_number_of_calls(request, 1)
