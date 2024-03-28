#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import pytest


@pytest.fixture
def config() -> Mapping[str, Any]:
    return {
        "start_date": "2020-10-01T00:00:00Z",
        "subdomain": "",
        "credentials": {
            "credentials": "access_token",
            "access_token": "__access_token__"
        }
    }


@pytest.fixture
def bans_stream_record() -> Mapping[str, Any]:
    return {
        "ip_address": [
            {
                "reason": "test",
                "type": "ip_address",
                "id": 1234,
                "created_at": "2021-04-21T14:42:46Z",
                "ip_address": "0.0.0.0"
            }
        ],
        "visitor": [
            {
                "type": "visitor",
                "id": 4444,
                "visitor_name": "Visitor 4444",
                "visitor_id": "visitor_id",
                "reason": "test",
                "created_at": "2021-04-27T13:25:01Z"
            }
        ]
    }


@pytest.fixture
def bans_stream_record_extractor_expected_output() -> List[Mapping[str, Any]]:
    return [
        {
            "reason": "test",
            "type": "ip_address",
            "id": 1234,
            "created_at": "2021-04-21T14:42:46Z",
            "ip_address": "0.0.0.0"
        },
        {
            "type": "visitor",
            "id": 4444,
            "visitor_name": "Visitor 4444",
            "visitor_id": "visitor_id",
            "reason": "test",
            "created_at": "2021-04-27T13:25:01Z"
        },
    ]
