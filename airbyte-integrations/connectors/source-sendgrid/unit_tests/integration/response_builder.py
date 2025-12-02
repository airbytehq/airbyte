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


def error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    error_messages = {
        HTTPStatus.UNAUTHORIZED: {"errors": [{"message": "Unauthorized"}]},
        HTTPStatus.FORBIDDEN: {"errors": [{"message": "Forbidden"}]},
        HTTPStatus.TOO_MANY_REQUESTS: {"errors": [{"message": "Rate limit exceeded"}]},
        HTTPStatus.NOT_FOUND: {"errors": [{"message": "Not found"}]},
    }
    body = error_messages.get(status_code, {"errors": [{"message": "Unknown error"}]})
    return build_response(body=body, status_code=status_code)


# Suppression streams responses (bounces, spam_reports, global_suppressions, blocks, invalid_emails)
def bounces_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "created": 1704067200,
                "email": "test@example.com",
                "reason": "550 5.1.1 The email account does not exist",
                "status": "5.1.1",
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


def spam_reports_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "created": 1704067200,
                "email": "spam@example.com",
                "ip": "192.168.1.1",
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


def global_suppressions_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "created": 1704067200,
                "email": "unsubscribed@example.com",
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


def blocks_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "created": 1704067200,
                "email": "blocked@example.com",
                "reason": "Connection timed out",
                "status": "4.0.0",
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


def invalid_emails_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "created": 1704067200,
                "email": "invalid@example",
                "reason": "Mail domain mentioned in email address is unknown",
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


# Suppression groups responses
def suppression_groups_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": 123,
                "name": "Test Group",
                "description": "Test suppression group",
                "is_default": False,
                "unsubscribes": 10,
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


def suppression_group_members_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "group_id": 123,
                "group_name": "Test Group",
                "email": "member@example.com",
                "created_at": 1704067200,
            }
        ]
    return build_response(body=records, status_code=HTTPStatus.OK)


# Marketing streams responses
def lists_response(
    records: Optional[List[Dict[str, Any]]] = None,
    next_page_url: Optional[str] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "list-id-123",
                "name": "Test List",
                "contact_count": 100,
                "_metadata": {"self": "https://api.sendgrid.com/v3/marketing/lists/list-id-123"},
            }
        ]
    body: Dict[str, Any] = {"result": records}
    if next_page_url:
        body["_metadata"] = {"next": next_page_url}
    else:
        body["_metadata"] = {}
    return build_response(body=body, status_code=HTTPStatus.OK)


def segments_response(
    records: Optional[List[Dict[str, Any]]] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "segment-id-123",
                "name": "Test Segment",
                "contacts_count": 50,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "sample_updated_at": "2024-01-15T00:00:00Z",
                "next_sample_update": "2024-01-16T00:00:00Z",
                "parent_list_ids": [],
                "query_version": "2.0",
                "status": {"query_validation": "valid"},
            }
        ]
    body = {"results": records}
    return build_response(body=body, status_code=HTTPStatus.OK)


def singlesend_stats_response(
    records: Optional[List[Dict[str, Any]]] = None,
    next_page_url: Optional[str] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "ab_phase": "all",
                "ab_variation": "",
                "aggregation": "total",
                "stats": {
                    "bounce_drops": 0,
                    "bounces": 1,
                    "clicks": 10,
                    "delivered": 95,
                    "invalid_emails": 2,
                    "opens": 50,
                    "requests": 100,
                    "spam_report_drops": 0,
                    "spam_reports": 1,
                    "unique_clicks": 8,
                    "unique_opens": 40,
                    "unsubscribes": 3,
                },
            }
        ]
    body: Dict[str, Any] = {"results": records}
    if next_page_url:
        body["_metadata"] = {"next": next_page_url}
    else:
        body["_metadata"] = {}
    return build_response(body=body, status_code=HTTPStatus.OK)


def stats_automations_response(
    records: Optional[List[Dict[str, Any]]] = None,
    next_page_url: Optional[str] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "automation-id-123",
                "aggregation": "total",
                "step_id": "step-1",
                "stats": {
                    "bounce_drops": 0,
                    "bounces": 1,
                    "clicks": 5,
                    "delivered": 45,
                    "invalid_emails": 1,
                    "opens": 25,
                    "requests": 50,
                    "spam_report_drops": 0,
                    "spam_reports": 0,
                    "unique_clicks": 4,
                    "unique_opens": 20,
                    "unsubscribes": 2,
                },
            }
        ]
    body: Dict[str, Any] = {"results": records}
    if next_page_url:
        body["_metadata"] = {"next": next_page_url}
    else:
        body["_metadata"] = {}
    return build_response(body=body, status_code=HTTPStatus.OK)


def singlesends_response(
    records: Optional[List[Dict[str, Any]]] = None,
    next_page_url: Optional[str] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Test Single Send",
                "status": "draft",
                "categories": ["marketing"],
                "is_abtest": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "send_at": None,
            }
        ]
    body: Dict[str, Any] = {"result": records}
    if next_page_url:
        body["_metadata"] = {"next": next_page_url}
    else:
        body["_metadata"] = {}
    return build_response(body=body, status_code=HTTPStatus.OK)


def templates_response(
    records: Optional[List[Dict[str, Any]]] = None,
    next_page_url: Optional[str] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "template-id-123",
                "name": "Test Template",
                "generation": "dynamic",
                "updated_at": "2024-01-15T00:00:00Z",
                "versions": [],
            }
        ]
    body: Dict[str, Any] = {"result": records}
    if next_page_url:
        body["_metadata"] = {"next": next_page_url}
    else:
        body["_metadata"] = {}
    return build_response(body=body, status_code=HTTPStatus.OK)


def campaigns_response(
    records: Optional[List[Dict[str, Any]]] = None,
    next_page_url: Optional[str] = None,
) -> HttpResponse:
    if records is None:
        records = [
            {
                "id": "campaign-id-123",
                "name": "Test Campaign",
                "status": "draft",
                "channels": ["email"],
                "is_abtest": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
            }
        ]
    body: Dict[str, Any] = {"result": records}
    if next_page_url:
        body["_metadata"] = {"next": next_page_url}
    else:
        body["_metadata"] = {}
    return build_response(body=body, status_code=HTTPStatus.OK)


# Contacts stream responses (AsyncRetriever)
def contacts_export_create_response(export_id: str = "export-id-123") -> HttpResponse:
    body = {"id": export_id}
    return build_response(body=body, status_code=HTTPStatus.ACCEPTED)


def contacts_export_status_response(
    status: str = "ready",
    urls: Optional[List[str]] = None,
) -> HttpResponse:
    if urls is None:
        urls = ["https://sendgrid-contacts-export.s3.amazonaws.com/export-file.csv.gz"]
    body = {
        "id": "export-id-123",
        "status": status,
        "urls": urls if status == "ready" else [],
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


def empty_response() -> HttpResponse:
    return build_response(body=[], status_code=HTTPStatus.OK)
