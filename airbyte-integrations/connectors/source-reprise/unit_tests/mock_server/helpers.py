# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared fixtures for the source-reprise mock-server tests.

Every request the connector issues carries timestamps derived from `now_utc()`, so the
tests freeze time at `_NOW` and use a `start_time` close to it. With `start_time` set to
midnight of the frozen day, each `P1D` stream produces exactly one slice, which keeps the
mocked request set small and fully enumerable.
"""

import json
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


NOW = "2026-08-20T12:00:00Z"

# Derived from NOW by the manifest's `now_utc().strftime('%Y-%m-%d %H:%M:%S')` expressions.
END_TIMESTAMP = "2026-08-20 12:00:00"
# Config `start_time`; >= the `now_utc() - P18M` floor, so it is used verbatim as the cursor start.
START_TIMESTAMP = "2026-08-20 00:00:00"

API_TOKEN = "reprise-portal-api-token"
SESSION_TOKEN = "warehouse-jwt-session-token"

LOGIN_URL = "https://app.getreprise.com/api/warehouse/token"
PIPES_URL = "https://api.us-east.tinybird.co/v0/pipes"

PAGE_SIZE = 10000

# Per-stream constant request parameters declared in the manifest.
STREAM_REQUEST_PARAMS: Mapping[str, Mapping[str, str]] = {
    "replay_session_activity": {"visitor_key": "1", "visitor_company": "1"},
    "replay_session_summary": {},
    "replay_metrics": {},
    "replay_change_feed": {},
    "replicate_session_activity": {"viewer_pii": "1"},
}


def config(
    *,
    api_token: str = API_TOKEN,
    start_time: Optional[str] = START_TIMESTAMP,
    include_viewer_pii: Optional[bool] = None,
    internal_email_domains: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a connector config. Optional keys are omitted unless explicitly provided."""
    built: Dict[str, Any] = {"api_token": api_token}
    if start_time is not None:
        built["start_time"] = start_time
    if include_viewer_pii is not None:
        built["include_viewer_pii"] = include_viewer_pii
    if internal_email_domains is not None:
        built["internal_email_domains"] = internal_email_domains
    return built


def login_request(api_token: str = API_TOKEN) -> HttpRequest:
    """POST that exchanges the portal API token for a scoped warehouse JWT."""
    return HttpRequest(url=LOGIN_URL, headers={"Authorization": f"Bearer {api_token}"})


def login_response(session_token: str = SESSION_TOKEN) -> HttpResponse:
    return HttpResponse(json.dumps({"token": session_token}), 200)


def data_request(
    stream_name: str,
    *,
    offset: int = 0,
    session_token: str = SESSION_TOKEN,
    start: str = START_TIMESTAMP,
    end: str = END_TIMESTAMP,
) -> HttpRequest:
    """The exact Tinybird pipe request the connector issues for one slice/page."""
    params: Dict[str, str] = {
        # SessionTokenAuthenticator injects the warehouse JWT as a request parameter.
        "token": session_token,
        "limit": str(PAGE_SIZE),
        "offset": str(offset),
    }
    if stream_name == "replay_change_feed":
        # No step and no start/end request parameters; the cursor start is sent via start_time_option.
        params["since_ingested_at"] = start
    else:
        params["start_timestamp"] = start
        params["end_timestamp"] = end
    params.update(STREAM_REQUEST_PARAMS[stream_name])
    return HttpRequest(url=f"{PIPES_URL}/{stream_name}.json", query_params=params)


def data_response(records: List[Mapping[str, Any]]) -> HttpResponse:
    """Tinybird envelope: the connector extracts records from `data` and ignores `meta`."""
    body = {
        "meta": [{"name": "session_id", "type": "String"}],
        "data": records,
        "rows": len(records),
    }
    return HttpResponse(json.dumps(body), 200)
