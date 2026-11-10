# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


BASE_URL = "https://app.pennylane.com/api/external/v1"
PAGE_SIZE = 100


@dataclass(frozen=True)
class StreamSpec:
    name: str
    path: str
    records_field: str
    primary_key: str
    incremental: bool


STREAMS: List[StreamSpec] = [
    StreamSpec("supplier_invoices", "supplier_invoices", "invoices", "id", True),
    StreamSpec("suppliers", "suppliers", "suppliers", "source_id", True),
    StreamSpec("plan_items", "plan_items", "plan_items", "v2_id", False),
    StreamSpec("customers", "customers", "customers", "source_id", True),
    StreamSpec("customer_invoices", "customer_invoices", "invoices", "id", True),
    StreamSpec("products", "products", "products", "source_id", True),
    StreamSpec("category_groups", "category_groups", "category_groups", "id", False),
    StreamSpec("categories", "categories", "categories", "source_id", True),
    StreamSpec("customer_estimates", "customer_estimates", "estimates", "id", True),
]
INCREMENTAL_STREAMS = [stream for stream in STREAMS if stream.incremental]


def updated_at_filter(lower_bound: str) -> str:
    """The v1 `filter` query parameter: a bare JSON array of filter objects."""
    return json.dumps([{"field": "updated_at", "operator": "gteq", "value": lower_bound}])


def list_request(stream: StreamSpec, page: int, updated_since: Optional[str] = None) -> HttpRequest:
    # The first page is requested without `page`; later pages send the page number from the previous response.
    query_params: Dict[str, str] = {"per_page": str(PAGE_SIZE)}
    if page > 1:
        query_params["page"] = str(page)
    if updated_since is not None:
        query_params["filter"] = updated_at_filter(updated_since)
    return HttpRequest(url=f"{BASE_URL}/{stream.path}", query_params=query_params)


def list_response(stream: StreamSpec, records: List[Dict[str, Any]], current_page: int, total_pages: int) -> HttpResponse:
    body = {stream.records_field: records, "current_page": current_page, "total_pages": total_pages}
    return HttpResponse(body=json.dumps(body), status_code=200)


def record(stream: StreamSpec, record_id: str, updated_at: str = "2024-02-01T10:00:00.000Z", **fields: Any) -> Dict[str, Any]:
    return {stream.primary_key: record_id, "updated_at": updated_at, **fields}
