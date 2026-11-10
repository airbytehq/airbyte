# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Records shaped like the RevenueCat v2 OpenAPI responses conform to the discovered schemas."""

from typing import Any, Dict, List

import jsonschema
import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.helpers import read_stream, records_data
from mock_server.request_builder import RevenueCatRequestBuilder
from mock_server.streams import STREAMS, list_response, mock_ancestors


_MS = 1735689600000
_PRICE = {"currency": "USD", "gross": 9.99, "commission": 2.99, "tax": 0.0, "proceeds": 7.0}
_PRODUCT = {
    "object": "product",
    "id": "prod_1",
    "store_identifier": "monthly",
    "type": "subscription",
    "subscription": None,
    "one_time": None,
    "created_at": _MS,
    "app_id": "app_1",
    "display_name": None,
    "state": "active",
    "indicative_price": None,
}
_ENTITLEMENTS = {
    "object": "list",
    "items": [
        {
            "object": "entitlement",
            "project_id": "proj1",
            "id": "entl_1",
            "lookup_key": "premium",
            "display_name": "Premium",
            "created_at": _MS,
            "state": "active",
            "products": {"object": "list", "items": [_PRODUCT], "next_page": None, "url": "/v2/products"},
        }
    ],
    "next_page": None,
    "url": "/v2/entitlements",
}

_RECORDS: Dict[str, Dict[str, Any]] = {
    "projects": {
        "object": "project",
        "id": "proj1",
        "name": "App",
        "created_at": _MS,
        "icon_url": "https://example.com/icon.png",
        "icon_url_large": "https://example.com/icon_large.png",
    },
    "apps": {
        "object": "app",
        "id": "app_1",
        "name": "Stripe app",
        "created_at": _MS,
        "type": "stripe",
        "project_id": "proj1",
        "custom_url_scheme": None,
        "stripe": {"stripe_account_id": "acct_1"},
        "app_store": None,
        "mac_app_store": None,
        "rc_billing": None,
        "paddle": None,
    },
    "customers": {
        "object": "customer",
        "id": "$RCAnonymousID:abc",
        "project_id": "proj1",
        "first_seen_at": _MS,
        "last_seen_at": None,
        "last_seen_app_version": "1.0.0",
        "last_seen_country": "US",
        "last_seen_platform": "iOS",
        "last_seen_platform_version": "18.1",
        "experiment": None,
    },
    "customers_subscriptions": {
        "object": "subscription",
        "id": "sub_1",
        "customer_id": "cust_1",
        "original_customer_id": "cust_1",
        "product_id": None,
        "purchased_at": _MS,
        "starts_at": _MS,
        "ends_at": None,
        "current_period_starts_at": _MS,
        "current_period_ends_at": None,
        "gives_access": True,
        "pending_payment": False,
        "auto_renewal_status": "will_renew",
        "status": "active",
        "total_revenue_in_usd": _PRICE,
        "presented_offering_id": None,
        "entitlements": _ENTITLEMENTS,
        "environment": "production",
        "store": "app_store",
        "ownership": "purchased",
        "pending_changes": None,
        "management_url": None,
        "country": None,
        "redemption": None,
        "product_change": None,
    },
    "customers_purchases": {
        "object": "purchase",
        "id": "purch_1",
        "customer_id": "cust_1",
        "original_customer_id": "cust_1",
        "product_id": "prod_1",
        "purchased_at": _MS,
        "revenue_in_usd": _PRICE,
        "quantity": 1,
        "status": "owned",
        "presented_offering_id": None,
        "entitlements": _ENTITLEMENTS,
        "environment": "production",
        "store": "play_store",
        "ownership": "purchased",
        "country": None,
        "redemption": None,
    },
    "customers_active_entitlements": {"object": "customer.active_entitlement", "entitlement_id": "entl_1", "expires_at": None},
    "customers_aliases": {"object": "customer.alias", "id": "alias_1", "created_at": _MS},
    "customers_invoices": {
        "object": "invoice",
        "id": "inv_1",
        "total_amount": _PRICE,
        "line_items": [
            {
                "object": "invoice.line_item",
                "product_identifier": "monthly",
                "product_display_name": None,
                "product_duration": None,
                "quantity": 1,
                "unit_amount": _PRICE,
            }
        ],
        "issued_at": _MS,
        "paid_at": None,
        "invoice_url": None,
    },
    "entitlements": {
        "object": "entitlement",
        "id": "entl_1",
        "project_id": "proj1",
        "lookup_key": "premium",
        "display_name": "Premium",
        "created_at": _MS,
        "state": "active",
    },
    "entitlements_products": {
        **_PRODUCT,
        "one_time": {"is_consumable": True},
        "indicative_price": {"currency": "USD", "amount_micros": 9990000},
    },
    "offerings": {
        "object": "offering",
        "id": "ofrng_1",
        "project_id": "proj1",
        "lookup_key": "default",
        "display_name": "Default",
        "is_current": True,
        "created_at": _MS,
        "state": "active",
        "paywall_id": None,
        "metadata": None,
    },
    "offerings_packages": {
        "object": "package",
        "id": "pkge_1",
        "lookup_key": "$rc_monthly",
        "display_name": "Monthly",
        "position": 1,
        "created_at": _MS,
    },
    "offerings_packages_products": {"product": _PRODUCT, "eligibility_criteria": "all"},
    "products": {**_PRODUCT, "one_time": {"is_consumable": False}, "indicative_price": None},
    "metrics_overview": {
        "object": "overview_metric",
        "id": "active_trials",
        "name": "Active Trials",
        "description": "Active trials",
        "unit": "#",
        "period": "P0D",
        "value": 3,
        "last_updated_at": None,
        "last_updated_at_iso8601": "2025-01-01T00:00:00Z",
    },
}


def _undeclared_paths(data: Any, schema: Dict[str, Any], path: str = "") -> List[str]:
    """Return the paths of keys in `data` that the schema does not declare, at every nesting level."""
    if isinstance(data, dict):
        properties = schema.get("properties")
        if properties is None:
            return []
        missing = []
        for key, value in data.items():
            if key not in properties:
                missing.append(f"{path}.{key}")
            else:
                missing += _undeclared_paths(value, properties[key], f"{path}.{key}")
        return missing
    if isinstance(data, list) and isinstance(schema.get("items"), dict):
        return [p for item in data for p in _undeclared_paths(item, schema["items"], f"{path}[]")]
    return []


def _discovered_schema(stream: str) -> Dict[str, Any]:
    config = ConfigBuilder().build()
    catalog = discover(get_source(config=config), config).catalog.catalog
    return next(s.json_schema for s in catalog.streams if s.name == stream)


@pytest.mark.parametrize("stream", list(STREAMS))
def test_emitted_records_declare_every_field_and_match_discovered_types(stream: str) -> None:
    spec = STREAMS[stream]
    with HttpMocker() as http_mocker:
        (partition,) = mock_ancestors(http_mocker, stream, ["parent_a"])
        request = RevenueCatRequestBuilder.endpoint(spec.path(partition))
        if stream == "metrics_overview":
            request = request.without_query_params()
        http_mocker.get(request.build(), list_response(stream, [_RECORDS[stream]]))
        output = read_stream(stream)

    assert output.errors == []
    (emitted,) = records_data(output)
    schema = _discovered_schema(stream)
    jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(emitted)
    assert _undeclared_paths(emitted, schema) == []
