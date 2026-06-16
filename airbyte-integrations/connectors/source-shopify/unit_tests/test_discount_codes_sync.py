#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests_mock as rmock
from source_shopify.streams.streams import DiscountCodesSync

from airbyte_cdk.utils import AirbyteTracedException


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
    stream = DiscountCodesSync(auth_config)
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
    stream = DiscountCodesSync(auth_config)
    stream.CHILD_PAGE_SIZE = page_size
    url = _graphql_url()

    parent_node = _make_parent_node(100, codesCount={"count": total_codes})
    all_codes = [_make_code_node(1000 + i, f"CODE-{i:04d}") for i in range(total_codes)]

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
    stream = DiscountCodesSync(auth_config)
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
                {"json": _parent_response([parent_a, parent_b])},
                {"json": _child_response(codes_a[:2], has_next=True, end_cursor="c1")},
                {"json": _child_response(codes_a[2:])},
                {"json": _child_response(codes_b)},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 5
    a_records = [r for r in records if r["price_rule_id"] == 100]
    assert len(a_records) == 3
    assert [r["code"] for r in a_records] == ["A-0", "A-1", "A-2"]
    b_records = [r for r in records if r["price_rule_id"] == 200]
    assert len(b_records) == 2
    assert [r["code"] for r in b_records] == ["B-0", "B-1"]


def test_zero_code_parent(auth_config, time_sleep_mock):
    stream = DiscountCodesSync(auth_config)
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
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_a = _make_parent_node(100)
    parent_b = _make_parent_node(200)

    code_a = _make_code_node(1000, "A")
    code_b = _make_code_node(2000, "B")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_a], has_next=True, end_cursor="p1")},
                {"json": _child_response([code_a])},
                {"json": _parent_response([parent_b])},
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
    stream = DiscountCodesSync(auth_config)
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

    first_request_body = json.loads(m.request_history[0].text)
    variables = first_request_body["variables"]
    assert "updated_at:>='2023-06-01T00:00:00+00:00'" in variables.get("query", "")


def test_lookback_window_applied_to_state(time_sleep_mock):
    config = {
        "shop": "test_shop",
        "start_date": "2023-01-01",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "authenticator": None,
        "lookback_window_in_days": 3,
    }
    stream = DiscountCodesSync(config)
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

    first_request_body = json.loads(m.request_history[0].text)
    variables = first_request_body["variables"]
    assert "2023-06-07" in variables.get("query", ""), f"Expected lookback-adjusted date in query, got: {variables}"


def test_discount_code_app_typename_no_summary(auth_config, time_sleep_mock):
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100, typename="DiscountCodeApp")
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
    stream = DiscountCodesSync(auth_config)
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
    assert record_keys.issubset(schema_keys), f"Extra keys not in schema: {record_keys - schema_keys}"


def test_null_code_discount_skipped(auth_config, time_sleep_mock):
    """Parent node with codeDiscount=null should be silently skipped."""
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    null_parent = {
        "id": "gid://shopify/DiscountCodeNode/999",
        "codeDiscount": None,
    }
    valid_parent = _make_parent_node(100)
    code_node = _make_code_node(200, "VALID")

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([null_parent, valid_parent])},
                {"json": _child_response([code_node])},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 1
    assert records[0]["code"] == "VALID"


def test_extract_codes_connection_fallback(auth_config, time_sleep_mock):
    """When the codeDiscount union fragment has no nested `codes` key,
    _extract_codes_connection should fall back to the top-level `codes` key
    or return an empty connection."""
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100)

    # Child response where codeDiscount has no codes key at all
    no_codes_response = {
        "data": {
            "codeDiscountNode": {
                "codeDiscount": {"__typename": "DiscountCodeBasic"},
            }
        },
        "extensions": _EXTENSIONS,
    }

    with rmock.Mocker() as m:
        m.post(
            url,
            [
                {"json": _parent_response([parent_node])},
                {"json": no_codes_response},
            ],
        )
        records = list(stream.read_records(sync_mode=None))

    assert records == []


def test_null_total_sales(auth_config, time_sleep_mock):
    """Parent with totalSales=null should emit total_sales=None."""
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100, totalSales=None)
    code_node = _make_code_node(200, "NO-SALES")

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
    assert records[0]["total_sales"] is None


@pytest.mark.parametrize(
    "current_state,record_updated_at,expected_cursor",
    [
        pytest.param(
            {},
            "2023-08-01T00:00:00+00:00",
            "2023-08-01T00:00:00+00:00",
            id="empty_state_advances_to_record",
        ),
        pytest.param(
            {"updated_at": "2023-07-01T00:00:00+00:00"},
            "2023-08-01T00:00:00+00:00",
            "2023-08-01T00:00:00+00:00",
            id="older_state_advances_to_newer_record",
        ),
        pytest.param(
            {"updated_at": "2023-09-01T00:00:00+00:00"},
            "2023-08-01T00:00:00+00:00",
            "2023-09-01T00:00:00+00:00",
            id="newer_state_does_not_move_backwards",
        ),
    ],
)
def test_get_updated_state(auth_config, current_state, record_updated_at, expected_cursor):
    stream = DiscountCodesSync(auth_config)
    record = {"updated_at": record_updated_at}
    new_state = stream.get_updated_state(current_state, record)
    assert new_state == {"updated_at": expected_cursor}


def test_graphql_errors_non_throttled_raises(auth_config, time_sleep_mock):
    stream = DiscountCodesSync(auth_config)
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


@pytest.mark.parametrize(
    "error_code",
    [
        pytest.param("THROTTLED", id="THROTTLED"),
        pytest.param("MAX_COST_EXCEEDED", id="MAX_COST_EXCEEDED"),
    ],
)
def test_graphql_throttled_retries_then_succeeds(auth_config, time_sleep_mock, error_code):
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    throttle_response = {
        "errors": [{"message": "Rate limited", "extensions": {"code": error_code}}],
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
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    throttle_response = {
        "errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}],
        "data": None,
        "extensions": _EXTENSIONS,
    }

    with rmock.Mocker() as m:
        m.post(url, [{"json": throttle_response}] * 10)
        with pytest.raises(AirbyteTracedException, match="exceeded max retries"):
            list(stream.read_records(sync_mode=None))


def test_none_optional_fields(auth_config, time_sleep_mock):
    """Verify None-valued optional fields (ends_at, usage_limit) are emitted correctly."""
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100, endsAt=None, usageLimit=None)
    code_node = _make_code_node(200, "OPT-NONE")

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
    assert records[0]["ends_at"] is None
    assert records[0]["usage_limit"] is None


def test_string_total_sales_amount(auth_config, time_sleep_mock):
    """Shopify returns totalSales.amount as a string; verify it passes through."""
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100, totalSales={"amount": "250.00", "currencyCode": "USD"})
    code_node = _make_code_node(200, "STR-AMT")

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
    assert records[0]["total_sales"]["amount"] == 250.0
    assert records[0]["total_sales"]["currency_code"] == "USD"


def test_missing_end_cursor_breaks_child_loop(auth_config, time_sleep_mock):
    """hasNextPage=true with no endCursor should break the child loop instead of looping forever."""
    stream = DiscountCodesSync(auth_config)
    url = _graphql_url()

    parent_node = _make_parent_node(100)
    # Child response claims more pages but provides no endCursor
    bad_child = {
        "data": {
            "codeDiscountNode": {
                "codeDiscount": {
                    "codes": {
                        "pageInfo": {"hasNextPage": True, "endCursor": None},
                        "nodes": [_make_code_node(200, "ONLY")],
                    }
                }
            }
        },
        "extensions": _EXTENSIONS,
    }

    with rmock.Mocker() as m:
        m.post(url, [{"json": _parent_response([parent_node])}, {"json": bad_child}])
        records = list(stream.read_records(sync_mode=None))

    assert len(records) == 1
    assert records[0]["code"] == "ONLY"
