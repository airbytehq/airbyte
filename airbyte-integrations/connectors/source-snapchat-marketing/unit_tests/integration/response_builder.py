#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import copy
import json
from http import HTTPStatus
from typing import Any, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from .config import (
    AD_ACCOUNT_ID,
    AD_ID,
    ADSQUAD_ID,
    CAMPAIGN_ID,
    ORGANIZATION_ID,
)


def _set_nested_value(obj: Any, key: str, value: Any) -> bool:
    """Recursively set a value in a nested structure."""
    if isinstance(obj, dict):
        if key in obj:
            obj[key] = value
            return True
        for v in obj.values():
            if _set_nested_value(v, key, value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _set_nested_value(item, key, value):
                return True
    return False


def create_response(
    resource_name: str,
    status_code: int = 200,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create an HttpResponse from a JSON template file.

    Args:
        resource_name: Name of the JSON template file (without .json extension)
        status_code: HTTP status code for the response
        has_next: Whether to include pagination next_link
        next_link: The URL for the next page

    Returns:
        HttpResponse with the template body
    """
    body = copy.deepcopy(find_template(resource_name, __file__))

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=status_code)


def create_response_with_id(
    resource_name: str,
    record_id: str,
    status_code: int = 200,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create an HttpResponse from a JSON template with a specific record ID."""
    body = copy.deepcopy(find_template(resource_name, __file__))
    _set_nested_value(body, "id", record_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=status_code)


def create_empty_response(resource_name: str) -> HttpResponse:
    """Create an empty response for a given resource."""
    body = copy.deepcopy(find_template(resource_name, __file__))

    for key in body:
        if isinstance(body[key], list) and key not in ["request_status", "request_id"]:
            body[key] = []
            break

    return HttpResponse(body=json.dumps(body), status_code=200)


def create_error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    """Create an error response from a JSON template."""
    error_template_map = {
        HTTPStatus.UNAUTHORIZED: "error_401",
        HTTPStatus.TOO_MANY_REQUESTS: "error_429",
    }

    template_name = error_template_map.get(status_code)
    if template_name:
        body = copy.deepcopy(find_template(template_name, __file__))
    else:
        body = {"request_status": "ERROR", "request_id": "test_request_id", "msg": f"Error {status_code.value}"}

    return HttpResponse(body=json.dumps(body), status_code=status_code.value)


def create_oauth_response() -> HttpResponse:
    """Create an OAuth token response from JSON template."""
    body = copy.deepcopy(find_template("oauth_token", __file__))
    return HttpResponse(body=json.dumps(body), status_code=200)


def create_stats_response(
    resource_name: str,
    entity_id: str,
    granularity: str = "HOUR",
    status_code: int = 200,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a stats response with specific entity ID and granularity."""
    body = copy.deepcopy(find_template(resource_name, __file__))
    _set_nested_value(body, "id", entity_id)
    _set_nested_value(body, "granularity", granularity)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=status_code)


def create_multiple_records_response(
    resource_name: str,
    record_ids: List[str],
    status_code: int = 200,
) -> HttpResponse:
    """Create a response with multiple records for testing substreams with multiple parents."""
    template = find_template(resource_name, __file__)
    body = copy.deepcopy(template)

    data_key = None
    record_template = None
    for key in body:
        if isinstance(body[key], list) and key not in ["request_status", "request_id"]:
            data_key = key
            if body[key]:
                record_template = copy.deepcopy(body[key][0])
            break

    if data_key and record_template:
        body[data_key] = []
        for record_id in record_ids:
            record = copy.deepcopy(record_template)
            _set_nested_value(record, "id", record_id)
            body[data_key].append(record)

    return HttpResponse(body=json.dumps(body), status_code=status_code)


# Legacy helper functions that wrap the new template-based functions
# These maintain backward compatibility with existing tests


def oauth_response() -> HttpResponse:
    """Create an OAuth token response."""
    return create_oauth_response()


def organizations_response(
    organization_id: str = ORGANIZATION_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create an organizations response using JSON template."""
    return create_response_with_id("organizations", organization_id, has_next=has_next, next_link=next_link)


def adaccounts_response(
    ad_account_id: str = AD_ACCOUNT_ID,
    organization_id: str = ORGANIZATION_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create an adaccounts response using JSON template."""
    body = copy.deepcopy(find_template("adaccounts", __file__))
    _set_nested_value(body, "id", ad_account_id)
    _set_nested_value(body, "organization_id", organization_id)
    _set_nested_value(body, "advertiser_organization_id", organization_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def adaccounts_response_multiple(
    ad_account_ids: List[str],
    organization_id: str = ORGANIZATION_ID,
) -> HttpResponse:
    """Create response with multiple ad accounts for testing substreams with multiple parents."""
    return create_multiple_records_response("adaccounts", ad_account_ids)


def organizations_response_multiple(
    organization_ids: List[str],
) -> HttpResponse:
    """Create response with multiple organizations for testing substreams with multiple parents."""
    return create_multiple_records_response("organizations", organization_ids)


def adsquads_response_multiple(
    adsquad_ids: List[str],
) -> HttpResponse:
    """Create response with multiple adsquads for testing substreams with multiple parents."""
    return create_multiple_records_response("adsquads", adsquad_ids)


def creatives_response(
    creative_id: str = "test_creative_123",
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a creatives response using JSON template."""
    body = copy.deepcopy(find_template("creatives", __file__))
    _set_nested_value(body, "id", creative_id)
    _set_nested_value(body, "ad_account_id", ad_account_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def ads_response(
    ad_id: str = AD_ID,
    ad_account_id: str = AD_ACCOUNT_ID,
    adsquad_id: str = ADSQUAD_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create an ads response using JSON template."""
    body = copy.deepcopy(find_template("ads", __file__))
    _set_nested_value(body, "id", ad_id)
    _set_nested_value(body, "ad_squad_id", adsquad_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def adsquads_response(
    adsquad_id: str = ADSQUAD_ID,
    ad_account_id: str = AD_ACCOUNT_ID,
    campaign_id: str = CAMPAIGN_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create an adsquads response using JSON template."""
    body = copy.deepcopy(find_template("adsquads", __file__))
    _set_nested_value(body, "id", adsquad_id)
    _set_nested_value(body, "campaign_id", campaign_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def segments_response(
    segment_id: str = "test_segment_123",
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a segments response using JSON template."""
    body = copy.deepcopy(find_template("segments", __file__))
    _set_nested_value(body, "id", segment_id)
    _set_nested_value(body, "ad_account_id", ad_account_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def media_response(
    media_id: str = "test_media_123",
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a media response using JSON template."""
    body = copy.deepcopy(find_template("media", __file__))
    _set_nested_value(body, "id", media_id)
    _set_nested_value(body, "ad_account_id", ad_account_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def campaigns_response(
    campaign_id: str = CAMPAIGN_ID,
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a campaigns response using JSON template."""
    body = copy.deepcopy(find_template("campaigns", __file__))
    _set_nested_value(body, "id", campaign_id)
    _set_nested_value(body, "ad_account_id", ad_account_id)

    if has_next and next_link:
        body["paging"] = {"next_link": next_link}

    return HttpResponse(body=json.dumps(body), status_code=200)


def stats_timeseries_response(
    entity_id: str = AD_ACCOUNT_ID,
    granularity: str = "HOUR",
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a stats timeseries response using JSON template."""
    return create_stats_response("stats_timeseries", entity_id, granularity, has_next=has_next, next_link=next_link)


def stats_lifetime_response(
    entity_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    """Create a stats lifetime response using JSON template."""
    return create_stats_response("stats_lifetime", entity_id, "LIFETIME", has_next=has_next, next_link=next_link)


def error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    """Create an error response using JSON template."""
    return create_error_response(status_code)


def empty_response(stream_key: str = "organizations") -> HttpResponse:
    """Create an empty response for a given stream using JSON template."""
    return create_empty_response(stream_key)
