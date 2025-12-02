# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse


def build_response(
    body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
    status_code: HTTPStatus = HTTPStatus.OK,
    headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(body=json.dumps(body), status_code=status_code.value, headers=headers)


def customer_response(
    customer_id: str = "cust_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Customer stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "customer": {
                    "id": customer_id,
                    "first_name": "Test",
                    "last_name": "Customer",
                    "email": "test@example.com",
                    "updated_at": updated_at,
                    "created_at": 1704067200,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def customer_response_multiple(
    customer_ids: List[str],
    updated_at: int = 1705312800,
) -> HttpResponse:
    """Customer stream response with multiple records."""
    records = [
        {
            "customer": {
                "id": cid,
                "first_name": f"Test_{cid}",
                "last_name": "Customer",
                "email": f"{cid}@example.com",
                "updated_at": updated_at,
                "created_at": 1704067200,
            }
        }
        for cid in customer_ids
    ]
    body = {"list": records}
    return build_response(body=body, status_code=HTTPStatus.OK)


def contact_response(
    contact_id: str = "contact_123",
    customer_id: str = "cust_123",
) -> HttpResponse:
    """Contact stream response (substream of customer)."""
    body = {
        "list": [
            {
                "contact": {
                    "id": contact_id,
                    "first_name": "Contact",
                    "last_name": "Person",
                    "email": "contact@example.com",
                }
            }
        ],
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


def subscription_response(
    subscription_id: str = "sub_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Subscription stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "subscription": {
                    "id": subscription_id,
                    "customer_id": "cust_123",
                    "plan_id": "plan_123",
                    "status": "active",
                    "updated_at": updated_at,
                    "created_at": 1704067200,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def invoice_response(
    invoice_id: str = "inv_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Invoice stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "invoice": {
                    "id": invoice_id,
                    "customer_id": "cust_123",
                    "subscription_id": "sub_123",
                    "status": "paid",
                    "total": 10000,
                    "updated_at": updated_at,
                    "date": 1705312800,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def event_response(
    event_id: str = "ev_123",
    occurred_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Event stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "event": {
                    "id": event_id,
                    "event_type": "subscription_created",
                    "occurred_at": occurred_at,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def transaction_response(
    transaction_id: str = "txn_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Transaction stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "transaction": {
                    "id": transaction_id,
                    "customer_id": "cust_123",
                    "amount": 10000,
                    "type": "payment",
                    "status": "success",
                    "updated_at": updated_at,
                    "date": 1705312800,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def plan_response(
    plan_id: str = "plan_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Plan stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "plan": {
                    "id": plan_id,
                    "name": "Test Plan",
                    "price": 10000,
                    "period": 1,
                    "period_unit": "month",
                    "status": "active",
                    "updated_at": updated_at,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def addon_response(
    addon_id: str = "addon_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Addon stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "addon": {
                    "id": addon_id,
                    "name": "Test Addon",
                    "price": 500,
                    "type": "on_off",
                    "status": "active",
                    "updated_at": updated_at,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def coupon_response(
    coupon_id: str = "coupon_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Coupon stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "coupon": {
                    "id": coupon_id,
                    "name": "Test Coupon",
                    "discount_type": "percentage",
                    "discount_percentage": 10.0,
                    "status": "active",
                    "updated_at": updated_at,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def item_response(
    item_id: str = "item_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Item stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "item": {
                    "id": item_id,
                    "name": "Test Item",
                    "type": "plan",
                    "status": "active",
                    "updated_at": updated_at,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def item_response_multiple(
    item_ids: List[str],
    updated_at: int = 1705312800,
) -> HttpResponse:
    """Item stream response with multiple records."""
    records = [
        {
            "item": {
                "id": iid,
                "name": f"Test Item {iid}",
                "type": "plan",
                "status": "active",
                "updated_at": updated_at,
            }
        }
        for iid in item_ids
    ]
    body = {"list": records}
    return build_response(body=body, status_code=HTTPStatus.OK)


def attached_item_response(
    attached_item_id: str = "attached_123",
    item_id: str = "item_123",
) -> HttpResponse:
    """Attached item stream response (substream of item)."""
    body = {
        "list": [
            {
                "attached_item": {
                    "id": attached_item_id,
                    "parent_item_id": item_id,
                    "item_id": "child_item_123",
                    "type": "mandatory",
                    "quantity": 1,
                }
            }
        ],
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


def gift_response(
    gift_id: str = "gift_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Gift stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "gift": {
                    "id": gift_id,
                    "status": "claimed",
                    "updated_at": updated_at,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def credit_note_response(
    credit_note_id: str = "cn_123",
    updated_at: int = 1705312800,
    next_offset: Optional[str] = None,
) -> HttpResponse:
    """Credit note stream response."""
    body: Dict[str, Any] = {
        "list": [
            {
                "credit_note": {
                    "id": credit_note_id,
                    "customer_id": "cust_123",
                    "total": 5000,
                    "status": "refunded",
                    "updated_at": updated_at,
                    "date": 1705312800,
                }
            }
        ],
    }
    if next_offset:
        body["next_offset"] = next_offset
    return build_response(body=body, status_code=HTTPStatus.OK)


def empty_response() -> HttpResponse:
    """Empty response with no records."""
    body = {"list": []}
    return build_response(body=body, status_code=HTTPStatus.OK)


def error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    """Error response for testing error handling."""
    error_messages = {
        HTTPStatus.UNAUTHORIZED: {"message": "Unauthorized", "api_error_code": "unauthorized"},
        HTTPStatus.FORBIDDEN: {"message": "Forbidden", "api_error_code": "forbidden"},
        HTTPStatus.TOO_MANY_REQUESTS: {"message": "Rate limit exceeded", "api_error_code": "rate_limit_exceeded"},
        HTTPStatus.NOT_FOUND: {"message": "Not found", "api_error_code": "resource_not_found"},
    }
    body = error_messages.get(status_code, {"message": "Unknown error"})
    return build_response(body=body, status_code=status_code)


def configuration_incompatible_response() -> HttpResponse:
    """Response for configuration_incompatible error (IGNORE action)."""
    body = {
        "message": "Stream is available only for Product Catalog 1.0",
        "api_error_code": "configuration_incompatible",
    }
    return build_response(body=body, status_code=HTTPStatus.BAD_REQUEST)
