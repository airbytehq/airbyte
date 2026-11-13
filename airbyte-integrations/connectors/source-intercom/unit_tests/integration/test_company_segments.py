# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from unittest import TestCase

from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components

_STREAM_NAME = "company_segments"
_API_URL = "https://api.intercom.io"
_SCROLL_PARAM = "scroll-1"


def _source(config: Mapping[str, Any], catalog: Optional[ConfiguredAirbyteCatalog] = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _segment(segment_id: str) -> Dict[str, Any]:
    return {
        "type": "segment",
        "id": segment_id,
        "name": f"Segment {segment_id}",
        "created_at": 1700000000,
        "updated_at": 1700000000,
        "person_type": "user",
    }


def _mock_companies_and_segments(http_mocker: HttpMocker, memberships: Dict[str, List[str]]) -> None:
    companies = [{"type": "company", "id": company_id, "updated_at": 1700000000} for company_id in memberships]
    http_mocker.get(
        HttpRequest(f"{_API_URL}/companies/scroll"),
        HttpResponse(json.dumps({"type": "list", "data": companies, "scroll_param": _SCROLL_PARAM})),
    )
    http_mocker.get(
        HttpRequest(f"{_API_URL}/companies/scroll", query_params={"scroll_param": _SCROLL_PARAM}),
        HttpResponse(json.dumps({"type": "list", "data": [], "scroll_param": _SCROLL_PARAM})),
    )
    for company_id, segment_ids in memberships.items():
        http_mocker.get(
            HttpRequest(f"{_API_URL}/companies/{company_id}/segments"),
            HttpResponse(json.dumps({"type": "list", "data": [_segment(segment_id) for segment_id in segment_ids]})),
        )


class CompanySegmentsTest(TestCase):
    @HttpMocker()
    def test_when_segment_is_shared_then_each_record_carries_its_company(self, http_mocker: HttpMocker) -> None:
        _mock_companies_and_segments(http_mocker, {"company-a": ["segment-1"], "company-b": ["segment-1", "segment-2"]})
        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()

        output = entrypoint_read(_source(config, catalog), config, catalog)

        assert sorted((record.record.data["company_id"], record.record.data["id"]) for record in output.records) == [
            ("company-a", "segment-1"),
            ("company-b", "segment-1"),
            ("company-b", "segment-2"),
        ]

    def test_primary_key_is_company_and_segment(self) -> None:
        config = ConfigBuilder().build()

        output = discover(_source(config), config)

        stream = next(stream for stream in output.catalog.catalog.streams if stream.name == _STREAM_NAME)
        assert stream.source_defined_primary_key == [["company_id"], ["id"]]
