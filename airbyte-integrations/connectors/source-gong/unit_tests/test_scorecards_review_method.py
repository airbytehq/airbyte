# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for the `scorecards_review_method` option of the `answeredScorecards` stream.

Gong's `/v2/stats/activity/scorecards` only returns manually reviewed scorecards unless
`filter.reviewMethod` is sent. The option must default to `MANUAL` (historical behaviour) and
must coexist with the `filter.reviewFromDate` injected by the incremental cursor.
"""

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_BASE_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}

_RESPONSE = {
    "answeredScorecards": [
        {
            "answeredScorecardId": "1",
            "scorecardId": "10",
            "callId": "100",
            "reviewTime": "2024-01-02T10:00:00Z",
            "reviewMethod": "AUTOMATIC",
        }
    ],
    "records": {"totalRecords": 1, "currentPageSize": 1, "currentPageNumber": 0},
}


def _request_body(config) -> dict:
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream("answeredScorecards", SyncMode.incremental).build()
    with requests_mock.Mocker() as mocker:
        mocker.post("https://api.gong.io/v2/stats/activity/scorecards", json=_RESPONSE)
        read(source, config, catalog)
        assert mocker.called, "expected at least one request to /v2/stats/activity/scorecards"
        return mocker.request_history[0].json()


def test_review_method_defaults_to_manual():
    assert _request_body(_BASE_CONFIG)["filter"]["reviewMethod"] == "MANUAL"


@pytest.mark.parametrize("review_method", ["MANUAL", "AUTOMATIC", "BOTH"])
def test_review_method_is_forwarded(review_method):
    body = _request_body({**_BASE_CONFIG, "scorecards_review_method": review_method})
    assert body["filter"]["reviewMethod"] == review_method


def test_review_method_does_not_replace_incremental_filter():
    body = _request_body({**_BASE_CONFIG, "scorecards_review_method": "BOTH"})
    assert body["filter"]["reviewFromDate"].startswith("2024-01-01")
    assert body["filter"]["reviewMethod"] == "BOTH"
