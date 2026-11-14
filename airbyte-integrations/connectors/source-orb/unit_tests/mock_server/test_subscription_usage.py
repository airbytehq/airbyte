# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta, timezone

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
@pytest.mark.parametrize("start_date", ["2025-01-01T00:00:00Z", "2023-11-01T00:00:00Z"], ids=["one-day", "fourteen-months"])
def test_subscription_usage_read(get_source, grouping_key, plan_id, empty_usage, start_date) -> None:
    config = {"api_key": "test-token", "start_date": start_date, "end_date": "2025-01-02T00:00:00Z"}
    start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime(2025, 1, 2, tzinfo=timezone.utc)
    windows = []
    for offset in range(0, (now - start).days + 1, 30):
        window_start = start + timedelta(days=offset)
        window_end = min(window_start + timedelta(days=30) - timedelta(microseconds=1), now)
        windows.append((window_start.strftime("%Y-%m-%dT%H:%M:%S.%f%z"), window_end.strftime("%Y-%m-%dT%H:%M:%S.%f%z")))
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
    parent_params = {"limit": "50", "created_at[gte]": start.isoformat(), "created_at[lte]": "2025-01-02T00:00:00+00:00"}
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
                for window_start, window_end in windows:
                    params = {"granularity": "day", "timeframe_start": window_start, "timeframe_end": window_end}
                    if grouping_key:
                        params.update(group_by=grouping_key, billable_metric_id=f"metric-{index}-{metric}")
                    record = {
                        "id": f"usage-{index}-{metric}-{window_start}",
                        "billable_metric": {"id": f"metric-{index}-{metric}", "name": "API calls"},
                        "timeframe_start": window_start,
                        "timeframe_end": window_end,
                        "usage": [{"quantity": 5, "timeframe_start": window_start}],
                    }
                    if grouping_key:
                        record["metric_group"] = {"property_key": "region", "property_value": "west"}
                    usage_request = HttpRequest(f"https://api.billwithorb.com/v1/subscriptions/sub-{index}/usage", query_params=params)
                    requests.append(usage_request)
                    mocker.get(usage_request, HttpResponse(json.dumps({"data": [] if empty_usage else [record]})))
                    if not empty_usage:
                        expected.append(
                            {key: value for key, value in record.items() if key != "usage"} | {"grouping_key": grouping_key or ""}
                        )
        catalog = CatalogBuilder().with_stream("subscription_usage", SyncMode.full_refresh).build()
        output = read(get_source(config, catalog), config, catalog)
        assert sorted([message.record.data for message in output.records], key=lambda record: record["id"]) == sorted(
            expected, key=lambda record: record["id"]
        )
        assert not output.errors
        for request in requests:
            mocker.assert_number_of_calls(request, 1)
