# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest import TestCase

from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components

_STREAM_NAME = "sla_policies"
_DOMAIN = "a-domain.freshdesk.com"
_URL = f"https://{_DOMAIN}/api/v2/sla_policies?per_page=100"


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()


def _read() -> EntrypointOutput:
    catalog = _catalog()
    config = ConfigBuilder().domain(_DOMAIN).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=None)
    return entrypoint_read(source, config, catalog)


def _policy(**overrides: Any) -> Dict[str, Any]:
    policy = {
        "id": 1,
        "name": "Default SLA Policy",
        "description": "default policy",
        "active": True,
        "is_default": True,
        "position": 1,
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": "2022-01-01T00:00:00Z",
    }
    policy.update(overrides)
    return policy


def _response(policies: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps(policies), 200)


def _ids(output: EntrypointOutput) -> List[Any]:
    # The CDK drops null-valued keys when it serializes a record, so a null id is emitted as an absent key.
    return [record.record.data.get("id") for record in output.records]


class SlaPoliciesTest(TestCase):
    @HttpMocker()
    def test_given_string_id_when_read_then_id_is_cast_to_integer(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(_URL), _response([_policy(id="67000087191")]))

        output = _read()

        assert _ids(output) == [67000087191]
        assert isinstance(_ids(output)[0], int)

    @HttpMocker()
    def test_given_integer_id_when_read_then_id_is_unchanged(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(_URL), _response([_policy(id=67000087191)]))

        output = _read()

        assert _ids(output) == [67000087191]
        assert isinstance(_ids(output)[0], int)

    @HttpMocker()
    def test_given_non_numeric_id_when_read_then_id_is_passed_through(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(_URL), _response([_policy(id="abc")]))

        output = _read()

        assert _ids(output) == ["abc"]

    @HttpMocker()
    def test_given_null_id_when_read_then_id_is_not_cast(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(_URL), _response([_policy(id=None)]))

        output = _read()

        assert _ids(output) == [None]

    @HttpMocker()
    def test_given_missing_id_when_read_then_id_is_not_cast(self, http_mocker: HttpMocker) -> None:
        policy = _policy()
        del policy["id"]
        http_mocker.get(HttpRequest(_URL), _response([policy]))

        output = _read()

        assert _ids(output) == [None]

    @HttpMocker()
    def test_given_mixed_ids_when_read_then_every_id_is_integer(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(HttpRequest(_URL), _response([_policy(id="1"), _policy(id=2), _policy(id="67000087191")]))

        output = _read()

        assert _ids(output) == [1, 2, 67000087191]
        assert all(isinstance(record_id, int) for record_id in _ids(output))
