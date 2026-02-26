# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


MANIFEST_PATH = Path(__file__).parent.parent.parent / "source_google_ads" / "manifest.yaml"
API_BASE = "https://googleads.googleapis.com/v20"
OAUTH_URL = "https://www.googleapis.com/oauth2/v3/token"

REPORT_MAPPING = {
    "account_performance_report": "customer",
    "ad_group_ad_legacy": "ad_group_ad",
    "ad_group_bidding_strategy": "ad_group",
    "ad_listing_group_criterion": "ad_group_criterion",
    "campaign_real_time_bidding_settings": "campaign",
    "campaign_bidding_strategy": "campaign",
    "service_accounts": "customer",
}

_manifest_cache = None


def _load_manifest() -> dict:
    global _manifest_cache
    if _manifest_cache is None:
        _manifest_cache = yaml.safe_load(MANIFEST_PATH.read_text())
    return _manifest_cache


def get_schema_fields(stream_name: str) -> List[str]:
    manifest = _load_manifest()
    schema = manifest["schemas"][stream_name]
    return list(schema["properties"].keys())


def get_customer_client_query() -> str:
    manifest = _load_manifest()
    return manifest["definitions"]["customer_client"]["retriever"]["requester"]["request_body"]["value"]["query"].strip()


def get_customer_client_non_manager_query() -> str:
    manifest = _load_manifest()
    return manifest["definitions"]["customer_client_non_manager"]["retriever"]["requester"]["request_body"]["value"]["query"].strip()


TRANSFORMATION_FIELDS = {"deleted_at", "change_status.last_change_date_time"}


def build_full_refresh_query(stream_name: str, exclude_transformation_fields: bool = False) -> str:
    fields = get_schema_fields(stream_name)
    if exclude_transformation_fields:
        fields = [f for f in fields if f not in TRANSFORMATION_FIELDS]
    resource_name = REPORT_MAPPING.get(stream_name, stream_name)
    return f"SELECT {', '.join(fields)} FROM {resource_name}"


def build_incremental_query(stream_name: str, start_date: str, end_date: str) -> str:
    fields = get_schema_fields(stream_name)
    resource_name = REPORT_MAPPING.get(stream_name, stream_name)
    return (
        f"SELECT {', '.join(fields)} FROM {resource_name} "
        f"WHERE segments.date BETWEEN '{start_date}' AND '{end_date}' "
        f"ORDER BY segments.date ASC"
    )


def build_click_view_query(date: str) -> str:
    fields = get_schema_fields("click_view")
    return f"SELECT {', '.join(fields)} FROM click_view WHERE segments.date = '{date}'"


def build_stream_response(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(
        body=json.dumps([{"results": records}]),
        status_code=200,
    )


def build_empty_response() -> HttpResponse:
    return HttpResponse(
        body=json.dumps([{"results": []}]),
        status_code=200,
    )


def build_error_response(status_code: int, error_message: str = "error") -> HttpResponse:
    return HttpResponse(
        body=json.dumps([{"error": {"code": status_code, "message": error_message, "status": "ERROR"}}]),
        status_code=status_code,
    )


def build_accessible_accounts_response(customer_ids: List[str]) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"resourceNames": [f"customers/{cid}" for cid in customer_ids]}),
        status_code=200,
    )


def build_customer_client_response(
    customer_id: str,
    is_manager: bool = False,
    status: str = "ENABLED",
) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            [
                {
                    "results": [
                        {
                            "customerClient": {
                                "clientCustomer": f"customers/{customer_id}",
                                "level": "1",
                                "id": customer_id,
                                "manager": is_manager,
                                "timeZone": "America/New_York",
                                "status": status,
                            }
                        }
                    ]
                }
            ]
        ),
        status_code=200,
    )


def mock_oauth(
    http_mocker: HttpMocker,
    client_id: str = "test_client_id",
    client_secret: str = "test_client_secret",
    refresh_token: str = "test_refresh_token",
) -> None:
    body = f"grant_type=refresh_token" f"&client_id={client_id}" f"&client_secret={client_secret}" f"&refresh_token={refresh_token}"
    http_mocker.post(
        HttpRequest(url=OAUTH_URL, body=body),
        HttpResponse(
            body=json.dumps(
                {
                    "access_token": "test_access_token",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                }
            ),
            status_code=200,
        ),
    )


def mock_accessible_accounts(
    http_mocker: HttpMocker,
    developer_token: str = "test_developer_token",
    customer_ids: Optional[List[str]] = None,
) -> None:
    if customer_ids is None:
        customer_ids = ["1234567890"]
    http_mocker.get(
        HttpRequest(
            url=f"{API_BASE}/customers:listAccessibleCustomers",
            headers={
                "developer-token": developer_token,
            },
        ),
        build_accessible_accounts_response(customer_ids),
    )


def mock_customer_client(
    http_mocker: HttpMocker,
    accessible_customer_id: str = "1234567890",
    customer_id: str = "1234567890",
    is_manager: bool = False,
    developer_token: str = "test_developer_token",
) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{API_BASE}/customers/{accessible_customer_id}/googleAds:searchStream",
            body=json.dumps({"query": get_customer_client_query()}),
        ),
        build_customer_client_response(customer_id, is_manager=is_manager),
    )


def mock_customer_client_non_manager(
    http_mocker: HttpMocker,
    accessible_customer_id: str = "1234567890",
    customer_id: str = "1234567890",
    developer_token: str = "test_developer_token",
) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{API_BASE}/customers/{accessible_customer_id}/googleAds:searchStream",
            body=json.dumps({"query": get_customer_client_non_manager_query()}),
        ),
        build_customer_client_response(customer_id, is_manager=False),
    )


def mock_full_refresh_stream(
    http_mocker: HttpMocker,
    stream_name: str,
    customer_id: str = "1234567890",
    response: Optional[HttpResponse] = None,
) -> None:
    query = build_full_refresh_query(stream_name)
    http_mocker.post(
        HttpRequest(
            url=f"{API_BASE}/customers/{customer_id}/googleAds:searchStream",
            body=json.dumps({"query": query}),
        ),
        response or build_empty_response(),
    )


def mock_incremental_stream(
    http_mocker: HttpMocker,
    stream_name: str,
    customer_id: str = "1234567890",
    start_date: str = "2024-01-01",
    end_date: str = "2024-01-14",
    response: Optional[HttpResponse] = None,
) -> None:
    query = build_incremental_query(stream_name, start_date, end_date)
    http_mocker.post(
        HttpRequest(
            url=f"{API_BASE}/customers/{customer_id}/googleAds:searchStream",
            body=json.dumps({"query": query}),
        ),
        response or build_empty_response(),
    )


def setup_full_refresh_parent_mocks(
    http_mocker: HttpMocker,
    accessible_customer_id: str = "1234567890",
    customer_id: str = "1234567890",
) -> None:
    mock_oauth(http_mocker)
    mock_accessible_accounts(http_mocker, customer_ids=[accessible_customer_id])
    mock_customer_client(
        http_mocker,
        accessible_customer_id=accessible_customer_id,
        customer_id=customer_id,
    )


def setup_incremental_non_manager_parent_mocks(
    http_mocker: HttpMocker,
    accessible_customer_id: str = "1234567890",
    customer_id: str = "1234567890",
) -> None:
    mock_oauth(http_mocker)
    mock_accessible_accounts(http_mocker, customer_ids=[accessible_customer_id])
    mock_customer_client_non_manager(
        http_mocker,
        accessible_customer_id=accessible_customer_id,
        customer_id=customer_id,
    )
