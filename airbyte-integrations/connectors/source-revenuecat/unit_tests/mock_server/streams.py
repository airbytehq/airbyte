# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Stream topology and record fixtures shared by the mock server tests."""

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.request_builder import RevenueCatRequestBuilder


PROJECT_ID = "proj1"
CREATED_AT_MS = 1735689600000  # 2025-01-01T00:00:00Z, after the default start_date


@dataclass(frozen=True)
class StreamSpec:
    name: str
    cursor_field: Optional[str]
    parent: Optional[str] = None
    partition_field: Optional[str] = None
    added_fields: List[str] = field(default_factory=list)
    pk_field: str = "id"
    extractor: str = "items"

    def path(self, partition: Dict[str, str]) -> str:
        return _PATHS[self.name](partition)


_PATHS: Dict[str, Callable[[Dict[str, str]], str]] = {
    "projects": lambda p: "/projects",
    "apps": lambda p: f"/projects/{p['project_id']}/apps",
    "metrics_overview": lambda p: f"/projects/{p['project_id']}/metrics/overview",
    "customers": lambda p: f"/projects/{p['project_id']}/customers",
    "customers_subscriptions": lambda p: f"/projects/{p['project_id']}/customers/{p['customer_id']}/subscriptions",
    "customers_purchases": lambda p: f"/projects/{p['project_id']}/customers/{p['customer_id']}/purchases",
    "customers_active_entitlements": lambda p: f"/projects/{p['project_id']}/customers/{p['customer_id']}/active_entitlements",
    "customers_aliases": lambda p: f"/projects/{p['project_id']}/customers/{p['customer_id']}/aliases",
    "customers_invoices": lambda p: f"/projects/{p['project_id']}/customers/{p['customer_id']}/invoices",
    "entitlements": lambda p: f"/projects/{p['project_id']}/entitlements",
    "entitlements_products": lambda p: f"/projects/{p['project_id']}/entitlements/{p['entitlement_id']}/products",
    "offerings": lambda p: f"/projects/{p['project_id']}/offerings",
    "offerings_packages": lambda p: f"/projects/{p['project_id']}/offerings/{p['offering_id']}/packages",
    "offerings_packages_products": lambda p: f"/projects/{p['project_id']}/packages/{p['package_id']}/products",
    "products": lambda p: f"/projects/{p['project_id']}/products",
}

_PROJECT_FK = ["project_id"]
_CUSTOMER_FK = ["project_id", "customer_id"]

STREAMS: Dict[str, StreamSpec] = {
    s.name: s
    for s in [
        StreamSpec("projects", "created_at"),
        StreamSpec("apps", "created_at", "projects", "project_id"),
        StreamSpec("metrics_overview", None, "projects", "project_id", _PROJECT_FK, extractor="metrics"),
        StreamSpec("customers", "last_seen_at", "projects", "project_id"),
        StreamSpec("customers_subscriptions", "starts_at", "customers", "customer_id", _PROJECT_FK),
        StreamSpec("customers_purchases", "purchased_at", "customers", "customer_id", _PROJECT_FK),
        StreamSpec("customers_active_entitlements", "expires_at", "customers", "customer_id", _CUSTOMER_FK, pk_field="entitlement_id"),
        StreamSpec("customers_aliases", "created_at", "customers", "customer_id", _CUSTOMER_FK),
        StreamSpec("customers_invoices", "issued_at", "customers", "customer_id", _CUSTOMER_FK),
        StreamSpec("entitlements", "created_at", "projects", "project_id"),
        StreamSpec("entitlements_products", "created_at", "entitlements", "entitlement_id", ["project_id", "entitlement_id"]),
        StreamSpec("offerings", "created_at", "projects", "project_id"),
        StreamSpec("offerings_packages", "created_at", "offerings", "offering_id", ["project_id", "offering_id"]),
        StreamSpec("offerings_packages_products", "created_at", "offerings_packages", "package_id", ["project_id", "package_id"]),
        StreamSpec("products", "created_at", "projects", "project_id", _PROJECT_FK),
    ]
}

LIST_STREAMS = [name for name in STREAMS if name != "metrics_overview"]
INCREMENTAL_STREAMS = [name for name, spec in STREAMS.items() if spec.cursor_field]


def record(stream: str, record_id: str, cursor_ms: int = CREATED_AT_MS) -> Dict[str, Any]:
    """A minimal vendor record for `stream` with its primary key and cursor value set."""
    spec = STREAMS[stream]
    if stream == "offerings_packages_products":
        return {"product": {"id": record_id, "created_at": cursor_ms, "object": "product"}, "eligibility_criteria": "all"}
    data: Dict[str, Any] = {spec.pk_field: record_id}
    if spec.cursor_field:
        data[spec.cursor_field] = cursor_ms
    return data


def list_response(stream: str, records: List[Dict[str, Any]], next_page: Optional[str] = None) -> HttpResponse:
    spec = STREAMS[stream]
    body: Dict[str, Any] = {"object": "list", spec.extractor: records, "next_page": next_page}
    if spec.extractor == "metrics":
        body = {"object": "overview_metrics", "metrics": records}
    return HttpResponse(body=json.dumps(body), status_code=200)


def mock_ancestors(http_mocker: HttpMocker, stream: str, parent_ids: List[str]) -> List[Dict[str, str]]:
    """
    Mock every ancestor of `stream`. The direct parent returns `parent_ids`; any other ancestor returns one record.

    Returns the partitions `stream` is read for, keyed like the manifest's `stream_partition`.
    """
    spec = STREAMS[stream]
    chain: List[StreamSpec] = []
    parent = spec.parent
    while parent:
        chain.insert(0, STREAMS[parent])
        parent = STREAMS[parent].parent
    if not chain:
        return [{}]

    partition: Dict[str, str] = {}
    for ancestor in chain:
        is_direct_parent = ancestor.name == spec.parent
        ids = parent_ids if is_direct_parent else [_default_id(ancestor.name)]
        http_mocker.get(
            RevenueCatRequestBuilder.endpoint(ancestor.path(partition)).build(),
            list_response(ancestor.name, [record(ancestor.name, i) for i in ids]),
        )
        if not is_direct_parent:
            partition = {**partition, _partition_key(ancestor.name): ids[0]}
    return [{**partition, spec.partition_field: parent_id} for parent_id in parent_ids]


def _default_id(stream: str) -> str:
    return PROJECT_ID if stream == "projects" else f"{stream}_1"


def _partition_key(stream: str) -> str:
    return {"projects": "project_id", "customers": "customer_id", "entitlements": "entitlement_id", "offerings": "offering_id"}[stream]
