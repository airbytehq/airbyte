# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from unittest import TestCase

import requests_mock
from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, TState, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
_SECONDS_PER_DAY = 86400

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def _catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def read(
    stream_name: str = "contacts",
    config_builder: Optional[ConfigBuilder] = None,
    state_builder: Optional[StateBuilder] = None,
) -> EntrypointOutput:
    catalog = _catalog(stream_name)
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state)


class ContactsTest(TestCase):
    def test_search_query_expands_sub_daily_interval_to_full_day_bounds(self) -> None:
        streams = {
            "contacts": ("contacts/search", "data"),
            "conversations": ("conversations/search", "conversations"),
            "tickets": ("tickets/search", "tickets"),
        }
        for stream_name, (path, response_field) in streams.items():
            with self.subTest(stream_name=stream_name):
                self._assert_search_query_expands_sub_daily_interval_to_full_day_bounds(stream_name, path, response_field)

    def test_search_query_keeps_30_day_checkpoint_slices_with_upper_bounds(self) -> None:
        streams = {
            "contacts": ("contacts/search", "data"),
            "conversations": ("conversations/search", "conversations"),
        }
        for stream_name, (path, response_field) in streams.items():
            with self.subTest(stream_name=stream_name):
                self._assert_search_query_keeps_30_day_checkpoint_slices_with_upper_bounds(stream_name, path, response_field)

    def _assert_search_query_expands_sub_daily_interval_to_full_day_bounds(self, stream_name: str, path: str, response_field: str) -> None:
        state_datetime = datetime.now(timezone.utc) - timedelta(hours=1)
        state_timestamp = int(state_datetime.timestamp())
        observed_bodies: List[Dict[str, Any]] = []

        def capture_request_body(request: requests_mock.request._RequestObjectProxy) -> bool:
            observed_bodies.append(json.loads(request.text))
            return True

        with requests_mock.Mocker() as http_mocker:
            http_mocker.post(
                f"https://api.intercom.io/{path}",
                additional_matcher=capture_request_body,
                json={
                    response_field: [
                        {
                            "id": f"{stream_name}_1",
                            "updated_at": state_timestamp + 60,
                        }
                    ],
                    "pages": {},
                },
            )

            output = read(
                stream_name=stream_name,
                state_builder=StateBuilder().with_stream_state(stream_name, {"updated_at": str(state_timestamp)}),
            )

        assert len(output.records) == 1
        assert len(observed_bodies) == 1

        query = observed_bodies[0]["query"]
        lower_bound_query = query["value"][0]
        upper_bound_query = query["value"][1]
        lower_bound = lower_bound_query["value"][0]["value"]
        inclusive_lower_bound = lower_bound_query["value"][1]["value"]

        expected_lower_bound = (state_timestamp // _SECONDS_PER_DAY) * _SECONDS_PER_DAY
        expected_upper_bound = ((int(datetime.now(timezone.utc).timestamp()) // _SECONDS_PER_DAY) * _SECONDS_PER_DAY) + (
            2 * _SECONDS_PER_DAY
        )
        assert query["operator"] == "AND"
        assert len(query["value"]) == 2
        assert lower_bound_query["operator"] == "OR"
        assert lower_bound == expected_lower_bound
        assert inclusive_lower_bound == expected_lower_bound
        assert upper_bound_query == {"field": "updated_at", "operator": "<", "value": expected_upper_bound}

    def _assert_search_query_keeps_30_day_checkpoint_slices_with_upper_bounds(
        self, stream_name: str, path: str, response_field: str
    ) -> None:
        start_datetime = datetime.now(timezone.utc) - timedelta(days=95)
        start_timestamp = int(start_datetime.timestamp())
        observed_bodies: List[Dict[str, Any]] = []

        def capture_request_body(request: requests_mock.request._RequestObjectProxy) -> bool:
            observed_bodies.append(json.loads(request.text))
            return True

        with requests_mock.Mocker() as http_mocker:
            http_mocker.post(
                f"https://api.intercom.io/{path}",
                additional_matcher=capture_request_body,
                json={
                    response_field: [
                        {
                            "id": f"{stream_name}_1",
                            "updated_at": start_timestamp + 60,
                        }
                    ],
                    "pages": {},
                },
            )

            output = read(
                stream_name=stream_name,
                config_builder=ConfigBuilder().start_date(start_datetime),
            )

        assert len(observed_bodies) >= 4
        assert 1 <= len(output.records) <= len(observed_bodies)
        assert [body["query"]["operator"] for body in observed_bodies] == ["AND"] * len(observed_bodies)
        assert [body["query"]["value"][1]["operator"] for body in observed_bodies] == ["<"] * len(observed_bodies)
