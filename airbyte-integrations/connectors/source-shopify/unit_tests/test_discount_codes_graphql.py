#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests_mock as rmock
from source_shopify.streams.streams import DiscountCodes

from airbyte_cdk.utils import AirbyteTracedException


@pytest.fixture
def auth_config():
    return {
        "shop": "test_shop",
        "start_date": "2023-01-01",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "authenticator": None,
    }


def _graphql_url(shop: str = "test_shop") -> str:
    return f"https://{shop}.myshopify.com/admin/api/2025-10/graphql.json"


_EXTENSIONS = {
    "cost": {
        "requestedQueryCost": 10,
        "actualQueryCost": 10,
        "throttleStatus": {
            "maximumAvailable": 2000.0,
            "currentlyAvailable": 1990,
            "restoreRate": 100.0,
        },
    }
}


def _parent_response(nodes, has_next=False, end_cursor=None):
    return {
        "data": {
            "codeDiscountNodes": {
                "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
                "nodes": nodes,
            }
        },
        "extensions": _EXTENSIONS,
    }


def _child_response(codes_nodes, has_next=False, end_cursor=None):
    """Build a child codes response with inline fragment structure."""
    codes_conn = {
        "codes": {
            "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
            "nodes": codes_nodes,
        }
    }
    return {
        "data": {
            "codeDiscountNode": {
                "codeDiscount": codes_conn,
            }
        },
        "extensions": _EXTENSIONS,
    }


def _make_parent_node(node_id, typename="DiscountCodeBasic", updated_at="2023-06-01T00:00:00Z", **extra):
    base = {
        "updatedAt": updated_at,
        "createdAt": "2023-01-01T00:00:00Z",
        "discountClass": "PRODUCT",
        "summary": "10% off",
        "startsAt": "2023-01-01T00:00:00Z",
        "endsAt": None,
        "status": "ACTIVE",
        "title": f"DISCOUNT-{node_id}",
        "usageLimit": None,
        "appliesOncePerCustomer": False,
        "asyncUsageCount": 5,
        "codesCount": {"count": 1},
        "totalSales": {"amount": 100.0, "currencyCode": "USD"},
    }
    base.update(extra)
    return {
        "id": f"gid://shopify/DiscountCodeNode/{node_id}",
        "codeDiscount": {"__typename": typename, **base},
    }


def _make_code_node(code_id, code_str="TESTCODE"):
    return {
        "id": f"gid://shopify/DiscountRedeemCode/{code_id}",
        "code": code_str,
        "asyncUsageCount": 0,
        "createdBy": None,
    }


def test_single_parent_single_child(auth_config, time_sleep_mock):
    """One parent with one child code produces one record with correct fields."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100)
    code_node = _make_code_node(200, "CODE-A")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": _child_response([code_node])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 1
    r = records[0]
    assert r["id"] == 200
    assert r["admin_graphql_api_id"] == "gid://shopify/DiscountRedeemCode/200"
    assert r["price_rule_id"] == 100
    assert r["code"] == "CODE-A"
    assert r["usage_count"] == 0
    assert r["discount_type"] == "PRODUCT"
    assert r["title"] == "DISCOUNT-100"
    assert r["status"] == "ACTIVE"
    assert r["total_sales"] == {"amount": 100.0, "currency_code": "USD"}
    assert r["shop_url"] == "test_shop"
    assert r["updated_at"] == "2023-06-01T00:00:00+00:00"
    assert r["created_at"] == "2023-01-01T00:00:00+00:00"


@pytest.mark.parametrize(
    "total_codes,page_size,expected_pages",
    [
        pytest.param(501, 250, 3, id="501_codes_3_pages"),
        pytest.param(250, 250, 1, id="exactly_one_full_page"),
    ],
)
def test_child_cursor_pagination(auth_config, time_sleep_mock, total_codes, page_size, expected_pages):
    """Child codes with >250 records are fetched across multiple pages."""
    stream = DiscountCodes(auth_config)
    stream.CHILD_PAGE_SIZE = page_size
    url = _graphql_url()

    parent_node = _make_parent_node(100, codesCount={"count": total_codes})
    all_codes = [_make_code_node(1000 + i, f"CODE-{i:04d}") for i in range(total_codes)]

    # Build paginated child responses
    child_responses = []
    for page_idx in range(expected_pages):
        start = page_idx * page_size
        end = min(start + page_size, total_codes)
        has_next = end < total_codes
        cursor = f"cursor-{page_idx}" if has_next else None
        child_responses.append({"json": _child_response(all_codes[start:end], has_next=has_next, end_cursor=cursor)})

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                *child_responses,
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == total_codes
    assert records[0]["code"] == "CODE-0000"
    assert records[-1]["code"] == f"CODE-{total_codes - 1:04d}"
    assert all(r["price_rule_id"] == 100 for r in records)


def test_two_parents_independent_child_cursors(auth_config, time_sleep_mock):
    """Two parents each have their own independent child pagination."""
    stream = DiscountCodes(auth_config)
    stream.CHILD_PAGE_SIZE = 2
    url = _graphql_url()

    parent_a = _make_parent_node(100, title="PARENT-A")
    parent_b = _make_parent_node(200, title="PARENT-B")

    codes_a = [_make_code_node(1000 + i, f"A-{i}") for i in range(3)]
    codes_b = [_make_code_node(2000 + i, f"B-{i}") for i in range(2)]

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                # parent page
                {"json": _parent_response([parent_a, parent_b])},
                # parent A child page 1 (2 codes, has next)
                {"json": _child_response(codes_a[:2], has_next=True, end_cursor="c1")},
                # parent A child page 2 (1 code, done)
                {"json": _child_response(codes_a[2:])},
                # parent B child page 1 (2 codes, done)
                {"json": _child_response(codes_b)},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 5
    # parent A records
    a_records = [r for r in records if r["price_rule_id"] == 100]
    assert len(a_records) == 3
    assert [r["code"] for r in a_records] == ["A-0", "A-1", "A-2"]
    # parent B records
    b_records = [r for r in records if r["price_rule_id"] == 200]
    assert len(b_records) == 2
    assert [r["code"] for r in b_records] == ["B-0", "B-1"]


def test_zero_code_parent(auth_config, time_sleep_mock):
    """A parent with no child codes produces zero records."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100, codesCount={"count": 0})

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": _child_response([])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert records == []


def test_parent_cursor_pagination(auth_config, time_sleep_mock):
    """Multiple pages of parents are fetched correctly."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    parent_a = _make_parent_node(100)
    parent_b = _make_parent_node(200)

    code_a = _make_code_node(1000, "A")
    code_b = _make_code_node(2000, "B")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                # parent page 1 (has next)
                {"json": _parent_response([parent_a], has_next=True, end_cursor="p1")},
                # child for parent A
                {"json": _child_response([code_a])},
                # parent page 2 (done)
                {"json": _parent_response([parent_b])},
                # child for parent B
                {"json": _child_response([code_b])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 2
    assert records[0]["code"] == "A"
    assert records[0]["price_rule_id"] == 100
    assert records[1]["code"] == "B"
    assert records[1]["price_rule_id"] == 200


def test_state_filters_parent_query(auth_config, time_sleep_mock):
    """Stream state is passed as a filter query on parent nodes."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100)
    code_node = _make_code_node(200, "C")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": _child_response([code_node])},
            ],
        )
        state = {"updated_at": "2023-06-01T00:00:00+00:00"}
        list(stream.read_records(sync_mode=None, stream_state=state))

    # Verify the parent query included the state filter
    first_request_body = json.loads(m.request_history[0].text)
    variables = first_request_body["variables"]
    assert "updated_at:>='2023-06-01T00:00:00+00:00'" in variables.get("query", "")


def test_lookback_window_applied_to_state(time_sleep_mock):
    """When lookback_window_in_days is configured, the state filter is adjusted backwards."""
    config = {
        "shop": "test_shop",
        "start_date": "2023-01-01",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "authenticator": None,
        "lookback_window_in_days": 3,
    }
    stream = DiscountCodes(config)
    url = _graphql_url()

    parent_node = _make_parent_node(100)
    code_node = _make_code_node(200, "C")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": _child_response([code_node])},
            ],
        )
        state = {"updated_at": "2023-06-10T00:00:00+00:00"}
        list(stream.read_records(sync_mode=None, stream_state=state))

    # With 3-day lookback, the filter should use 2023-06-07 instead of 2023-06-10
    first_request_body = json.loads(m.request_history[0].text)
    variables = first_request_body["variables"]
    assert "2023-06-07" in variables.get("query", ""), f"Expected lookback-adjusted date in query, got: {variables}"


def test_discount_code_app_typename_no_summary(auth_config, time_sleep_mock):
    """DiscountCodeApp type has no summary field; verify it emits None."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100, typename="DiscountCodeApp")
    # Remove summary since DiscountCodeApp doesn't have it
    del parent_node["codeDiscount"]["summary"]

    code_node = _make_code_node(200, "APP-CODE")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": _child_response([code_node])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 1
    assert records[0]["typename"] == "DiscountCodeApp"
    assert records[0]["summary"] is None


def test_schema_parity_with_json_schema(auth_config, time_sleep_mock):
    """All fields in the output match the discount_codes.json schema keys."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100)
    code_node = _make_code_node(200, "SCHEMA-TEST")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": _child_response([code_node])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    schema = stream.get_json_schema()
    schema_keys = set(schema["properties"].keys())
    record_keys = set(records[0].keys())

    # Every key in the record should be in the schema
    assert record_keys.issubset(schema_keys), f"Extra keys not in schema: {record_keys - schema_keys}"


def test_graphql_errors_non_throttled_raises(auth_config, time_sleep_mock):
    """Non-throttle GraphQL errors raise AirbyteTracedException immediately."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    error_response = {
        "errors": [{"message": "Field 'bogus' not found", "extensions": {"code": "FIELD_NOT_FOUND"}}],
        "data": None,
        "extensions": _EXTENSIONS,
    }

    with rmock.Mocker() as m:
        m.post(url, [{"json": error_response}])
        with pytest.raises(AirbyteTracedException, match="Field 'bogus' not found"):
            list(stream.read_records(sync_mode=None))


def test_graphql_throttled_retries_then_succeeds(auth_config, time_sleep_mock):
    """THROTTLED errors are retried; if a subsequent attempt succeeds, records are emitted."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    throttle_response = {
        "errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}],
        "data": None,
        "extensions": _EXTENSIONS,
    }

    parent_node = _make_parent_node(100)
    code_node = _make_code_node(200, "RETRY-OK")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": throttle_response},
                {"json": _parent_response([parent_node])},
                {"json": _child_response([code_node])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 1
    assert records[0]["code"] == "RETRY-OK"


def test_graphql_throttled_exhausts_retries(auth_config, time_sleep_mock):
    """THROTTLED errors exhaust retries and raise AirbyteTracedException."""
    stream = DiscountCodes(auth_config)
    url = _graphql_url()

    throttle_response = {
        "errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}],
        "data": None,
        "extensions": _EXTENSIONS,
    }

    with rmock.Mocker() as m:
        # Return throttled response for all retry attempts
        m.post(url, [{"json": throttle_response}] * 10)
        with pytest.raises(AirbyteTracedException, match="exceeded max retries"):
            list(stream.read_records(sync_mode=None))
