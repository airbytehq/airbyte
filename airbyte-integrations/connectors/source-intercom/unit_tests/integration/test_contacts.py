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


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("contacts", SyncMode.incremental).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def read(config_builder: Optional[ConfigBuilder] = None, state_builder: Optional[StateBuilder] = None) -> EntrypointOutput:
    catalog = _catalog()
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state)


class ContactsTest(TestCase):
    def test_search_query_expands_sub_daily_interval_to_day_boundaries(self) -> None:
        state_datetime = datetime.now(timezone.utc) - timedelta(hours=1)
        state_timestamp = int(state_datetime.timestamp())
        observed_bodies: List[Dict[str, Any]] = []

        def capture_request_body(request: requests_mock.request._RequestObjectProxy) -> bool:
            observed_bodies.append(json.loads(request.text))
            return True

        with requests_mock.Mocker() as http_mocker:
            http_mocker.post(
                "https://api.intercom.io/contacts/search",
                additional_matcher=capture_request_body,
                json={
                    "data": [
                        {
                            "id": "contact_1",
                            "updated_at": state_timestamp + 60,
                        }
                    ],
                    "pages": {},
                },
            )

            output = read(state_builder=StateBuilder().with_stream_state("contacts", {"updated_at": str(state_timestamp)}))

        assert len(output.records) == 1
        assert len(observed_bodies) == 1

        query = observed_bodies[0]["query"]
        lower_bound = query["value"][0]["value"][0]["value"]
        inclusive_lower_bound = query["value"][0]["value"][1]["value"]
        upper_bound = query["value"][1]["value"]

        expected_lower_bound = (state_timestamp // _SECONDS_PER_DAY) * _SECONDS_PER_DAY
        assert lower_bound == expected_lower_bound
        assert inclusive_lower_bound == expected_lower_bound
        assert upper_bound % _SECONDS_PER_DAY == 0
        assert 0 < upper_bound - int(datetime.now(timezone.utc).timestamp()) <= _SECONDS_PER_DAY
