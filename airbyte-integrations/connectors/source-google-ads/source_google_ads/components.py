#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config


logger = logging.getLogger("airbyte")


class AccessibleAccountsExtractor(RecordExtractor):
    """
    Custom extractor for the accessible accounts endpoint.
    The response is a list of strings instead of a list of objects.
    """
    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        response_data = response.json().get("resourceNames", [])
        if response_data:
            for resource_name in response_data:
                yield {"accessible_customer_id": resource_name.split("/")[-1]}


class GoogleAdsPerPartitionStateMigration(StateMigration):
    """
    Transforms the input state for per-partitioned streams from the legacy format to the low-code global cursor format.

    Example input state:
    {
      "1234567890": {"segments.date": "2120-10-10"}
    }
    Example output state:
    {
      "state": {"use_global_cursor": True, "segments.date": "2120-10-10"}
    }
    """

    config: Config

    def __init__(self, config: Config):
        self._config = config
        self._cursor_field = "segments.date"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state and "state" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        min_state = min(stream_state.values(), key=lambda state: state[self._cursor_field])
        return {"use_global_cursor": True, "state": min_state}
