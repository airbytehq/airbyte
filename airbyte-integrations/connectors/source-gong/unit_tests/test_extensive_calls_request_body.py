# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests verifying the `extensiveCalls` request body includes context fields.

Gong's `/v2/calls/extensive` API defaults `contentSelector.context` to `None`,
which omits context data from responses. The manifest must explicitly request
`context: "Extended"` with `contextTiming` values so that context fields are
returned in sync results.
"""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}

_EXTENSIVE_CALL_RESPONSE = {
    "calls": [
        {
            "metaData": {
                "id": "call-1",
                "url": "https://us-20768.app.gong.io/call?id=call-1",
                "title": "Test call",
                "scheduled": "2024-01-02T10:00:00Z",
                "started": "2024-01-02T10:00:00Z",
                "duration": 120,
                "direction": "Inbound",
                "isPrivate": False,
            },
        }
    ],
    "records": {"totalRecords": 1, "currentPageSize": 1, "currentPageNumber": 0},
}


def test_extensive_calls_request_includes_context_extended():
    """The POST body for `extensiveCalls` must set `contentSelector.context` to `Extended`."""
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("extensiveCalls", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.post("https://api.gong.io/v2/calls/extensive", json=_EXTENSIVE_CALL_RESPONSE)
        read(source, _CONFIG, catalog)

        assert mocker.called, "expected at least one request to /v2/calls/extensive"
        request_body = mocker.last_request.json()

    content_selector = request_body["contentSelector"]
    assert (
        content_selector["context"] == "Extended"
    ), f"expected contentSelector.context='Extended', got {content_selector.get('context')!r}"


def test_extensive_calls_request_includes_context_timing():
    """The POST body must include both `Now` and `TimeOfCall` in `contextTiming`."""
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("extensiveCalls", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker:
        mocker.post("https://api.gong.io/v2/calls/extensive", json=_EXTENSIVE_CALL_RESPONSE)
        read(source, _CONFIG, catalog)

        request_body = mocker.last_request.json()

    content_selector = request_body["contentSelector"]
    assert sorted(content_selector["contextTiming"]) == [
        "Now",
        "TimeOfCall",
    ], f"expected contextTiming=['Now', 'TimeOfCall'], got {content_selector.get('contextTiming')!r}"
