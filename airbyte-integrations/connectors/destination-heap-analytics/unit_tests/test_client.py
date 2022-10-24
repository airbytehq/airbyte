#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from json import load
from typing import Dict

from destination_heap_analytics.client import HeapClient
from pytest import fixture


@fixture(scope="module")
def config_events() -> Dict[str, str]:
    with open(
        "sample_files/config-events.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def config_aap() -> Dict[str, str]:
    with open(
        "sample_files/config-aap.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def config_aup() -> Dict[str, str]:
    with open(
        "sample_files/config-aup.json",
    ) as f:
        yield load(f)


class TestHeapClient:
    def test_constructor(self, config_events, config_aup, config_aap):
        client = HeapClient(**config_events)
        assert client.app_id == "11"
        assert client.api_type == "track"
        assert client.check_endpoint == "https://heapanalytics.com/api/track"
        assert client.api_endpoint == "https://heapanalytics.com/api/track"

        client = HeapClient(**config_aup)
        assert client.app_id == "11"
        assert client.api_type == "add_user_properties"
        assert client.check_endpoint == "https://heapanalytics.com/api/track"
        assert client.api_endpoint == "https://heapanalytics.com/api/add_user_properties"

        client = HeapClient(**config_aap)
        assert client.app_id == "11"
        assert client.api_type == "add_account_properties"
        assert client.check_endpoint == "https://heapanalytics.com/api/track"
        assert client.api_endpoint == "https://heapanalytics.com/api/add_account_properties"
