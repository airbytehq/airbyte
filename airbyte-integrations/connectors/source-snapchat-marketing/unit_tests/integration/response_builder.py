#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse

from .config import (
    AD_ACCOUNT_ID,
    AD_ID,
    ADSQUAD_ID,
    CAMPAIGN_ID,
    ORGANIZATION_ID,
)


def build_response(
    body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
    status_code: HTTPStatus = HTTPStatus.OK,
    headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(body=json.dumps(body), status_code=status_code.value, headers=headers)


def oauth_response() -> HttpResponse:
    body = {
        "access_token": "test_access_token",
        "token_type": "Bearer",
        "expires_in": 1800,
        "refresh_token": "test_refresh_token",
        "scope": "snapchat-marketing-api",
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


def organizations_response(
    organization_id: str = ORGANIZATION_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "organizations": [
            {
                "sub_request_status": "SUCCESS",
                "organization": {
                    "id": organization_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Organization",
                    "address_line_1": "123 Test St",
                    "locality": "Test City",
                    "administrative_district_level_1": "CA",
                    "country": "US",
                    "postal_code": "12345",
                    "type": "ENTERPRISE",
                    "state": "ACTIVE",
                    "configuration_settings": {},
                    "accepted_term_version": "1",
                    "contact_name": "Test Contact",
                    "contact_email": "test@example.com",
                    "contact_phone": "+1234567890",
                    "roles": ["ADMIN"],
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def adaccounts_response(
    ad_account_id: str = AD_ACCOUNT_ID,
    organization_id: str = ORGANIZATION_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "adaccounts": [
            {
                "sub_request_status": "SUCCESS",
                "adaccount": {
                    "id": ad_account_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Ad Account",
                    "type": "PARTNER",
                    "status": "ACTIVE",
                    "organization_id": organization_id,
                    "currency": "USD",
                    "timezone": "America/Los_Angeles",
                    "advertiser_organization_id": organization_id,
                    "advertiser": "Test Advertiser",
                    "billing_type": "IO",
                    "billing_center_id": "test_billing_center",
                    "lifetime_spend_cap_micro": 0,
                    "agency_representing_client": False,
                    "client_paying_invoices": False,
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def adaccounts_response_multiple(
    ad_account_ids: List[str],
    organization_id: str = ORGANIZATION_ID,
) -> HttpResponse:
    """Create response with multiple ad accounts for testing substreams with multiple parents."""
    adaccounts = []
    for ad_account_id in ad_account_ids:
        adaccounts.append(
            {
                "sub_request_status": "SUCCESS",
                "adaccount": {
                    "id": ad_account_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": f"Test Ad Account {ad_account_id}",
                    "type": "PARTNER",
                    "status": "ACTIVE",
                    "organization_id": organization_id,
                    "currency": "USD",
                    "timezone": "America/Los_Angeles",
                    "advertiser_organization_id": organization_id,
                    "advertiser": "Test Advertiser",
                    "billing_type": "IO",
                    "billing_center_id": "test_billing_center",
                    "lifetime_spend_cap_micro": 0,
                    "agency_representing_client": False,
                    "client_paying_invoices": False,
                },
            }
        )
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "adaccounts": adaccounts,
    }
    return build_response(body=body, status_code=HTTPStatus.OK)


def creatives_response(
    creative_id: str = "test_creative_123",
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "creatives": [
            {
                "sub_request_status": "SUCCESS",
                "creative": {
                    "id": creative_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Creative",
                    "ad_account_id": ad_account_id,
                    "type": "SNAP_AD",
                    "packaging_status": "SUCCESS",
                    "review_status": "APPROVED",
                    "shareable": True,
                    "headline": "Test Headline",
                    "brand_name": "Test Brand",
                    "call_to_action": "INSTALL_NOW",
                    "top_snap_media_id": "test_media_id",
                    "top_snap_crop_position": "MIDDLE",
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def ads_response(
    ad_id: str = AD_ID,
    ad_account_id: str = AD_ACCOUNT_ID,
    adsquad_id: str = ADSQUAD_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "ads": [
            {
                "sub_request_status": "SUCCESS",
                "ad": {
                    "id": ad_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Ad",
                    "ad_squad_id": adsquad_id,
                    "creative_id": "test_creative_123",
                    "status": "ACTIVE",
                    "type": "SNAP_AD",
                    "render_type": "STATIC",
                    "review_status": "APPROVED",
                    "review_status_reasons": [],
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def adsquads_response(
    adsquad_id: str = ADSQUAD_ID,
    ad_account_id: str = AD_ACCOUNT_ID,
    campaign_id: str = CAMPAIGN_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "adsquads": [
            {
                "sub_request_status": "SUCCESS",
                "adsquad": {
                    "id": adsquad_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Ad Squad",
                    "status": "ACTIVE",
                    "campaign_id": campaign_id,
                    "type": "SNAP_ADS",
                    "targeting": {},
                    "targeting_reach_status": "VALID",
                    "placement": "SNAP_ADS",
                    "billing_event": "IMPRESSION",
                    "auto_bid": True,
                    "bid_strategy": "AUTO_BID",
                    "daily_budget_micro": 50000000,
                    "start_time": "2024-01-01T00:00:00.000Z",
                    "optimization_goal": "IMPRESSIONS",
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def segments_response(
    segment_id: str = "test_segment_123",
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "segments": [
            {
                "sub_request_status": "SUCCESS",
                "segment": {
                    "id": segment_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Segment",
                    "ad_account_id": ad_account_id,
                    "description": "Test segment description",
                    "status": "ACTIVE",
                    "source_type": "FIRST_PARTY",
                    "retention_in_days": 180,
                    "approximate_number_users": 1000,
                    "upload_status": "COMPLETE",
                    "targetable_status": "READY",
                    "organization_id": ORGANIZATION_ID,
                    "visible_to": ["ALL_ACCOUNTS"],
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def media_response(
    media_id: str = "test_media_123",
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "media": [
            {
                "sub_request_status": "SUCCESS",
                "media": {
                    "id": media_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Media",
                    "ad_account_id": ad_account_id,
                    "type": "VIDEO",
                    "media_status": "READY",
                    "file_name": "test_video.mp4",
                    "download_link": "https://example.com/test_video.mp4",
                    "duration_secs": 10.5,
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def campaigns_response(
    campaign_id: str = CAMPAIGN_ID,
    ad_account_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "campaigns": [
            {
                "sub_request_status": "SUCCESS",
                "campaign": {
                    "id": campaign_id,
                    "updated_at": "2024-01-15T10:00:00.000Z",
                    "created_at": "2023-01-01T00:00:00.000Z",
                    "name": "Test Campaign",
                    "ad_account_id": ad_account_id,
                    "status": "ACTIVE",
                    "objective": "AWARENESS",
                    "start_time": "2024-01-01T00:00:00.000Z",
                    "end_time": "2024-12-31T23:59:59.000Z",
                    "daily_budget_micro": 100000000,
                    "lifetime_spend_cap_micro": 0,
                    "buy_model": "AUCTION",
                    "regulations": {},
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def stats_timeseries_response(
    entity_id: str = AD_ACCOUNT_ID,
    granularity: str = "HOUR",
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "timeseries_stats": [
            {
                "sub_request_status": "SUCCESS",
                "timeseries_stat": {
                    "id": entity_id,
                    "type": "AD_ACCOUNT",
                    "granularity": granularity,
                    "start_time": "2024-01-15T00:00:00.000-0800",
                    "end_time": "2024-01-15T01:00:00.000-0800",
                    "timeseries": [
                        {
                            "start_time": "2024-01-15T00:00:00.000-0800",
                            "end_time": "2024-01-15T01:00:00.000-0800",
                            "stats": {
                                "impressions": 1000,
                                "swipes": 50,
                                "spend": 5000000,
                                "video_views": 800,
                                "android_installs": 10,
                                "ios_installs": 15,
                                "total_installs": 25,
                            },
                        }
                    ],
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def stats_lifetime_response(
    entity_id: str = AD_ACCOUNT_ID,
    has_next: bool = False,
    next_link: Optional[str] = None,
) -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        "lifetime_stats": [
            {
                "sub_request_status": "SUCCESS",
                "lifetime_stat": {
                    "id": entity_id,
                    "type": "AD_ACCOUNT",
                    "granularity": "LIFETIME",
                    "stats": {
                        "impressions": 100000,
                        "swipes": 5000,
                        "spend": 500000000,
                        "video_views": 80000,
                        "android_installs": 1000,
                        "ios_installs": 1500,
                        "total_installs": 2500,
                    },
                },
            }
        ],
    }
    if has_next and next_link:
        body["paging"] = {"next_link": next_link}
    return build_response(body=body, status_code=HTTPStatus.OK)


def error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    error_messages = {
        HTTPStatus.UNAUTHORIZED: {"request_status": "ERROR", "request_id": "test_request_id", "msg": "Unauthorized"},
        HTTPStatus.FORBIDDEN: {"request_status": "ERROR", "request_id": "test_request_id", "msg": "Forbidden"},
        HTTPStatus.TOO_MANY_REQUESTS: {"request_status": "ERROR", "request_id": "test_request_id", "msg": "Rate limit exceeded"},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"request_status": "ERROR", "request_id": "test_request_id", "msg": "Internal server error"},
    }
    body = error_messages.get(status_code, {"request_status": "ERROR", "msg": "Unknown error"})
    return build_response(body=body, status_code=status_code)


def empty_response(stream_key: str = "organizations") -> HttpResponse:
    body = {
        "request_status": "SUCCESS",
        "request_id": "test_request_id",
        stream_key: [],
    }
    return build_response(body=body, status_code=HTTPStatus.OK)
