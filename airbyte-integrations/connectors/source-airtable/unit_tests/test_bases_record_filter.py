# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Mapping

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.models.declarative_component_schema import RecordSelector as RecordSelectorModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


CONFIG = {"credentials": {"auth_method": "api_key", "api_key": "test-key"}}
VALID_PERMISSION_LEVELS = ["none", "read", "comment", "edit", "create", "interfaceOnly"]


@pytest.fixture(scope="module")
def bases_record_selector(manifest_path: Path) -> RecordSelector:
    manifest = yaml.safe_load(manifest_path.read_text())
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    propagated = ManifestComponentTransformer().propagate_types_and_parameters("", resolved, {})
    selector_definition = propagated["definitions"]["streams"]["bases"]["retriever"]["record_selector"]
    return ModelToComponentFactory().create_component(RecordSelectorModel, selector_definition, CONFIG, name="bases")


def _response(bases: list[Mapping[str, Any]]) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({"bases": bases}).encode("utf-8")
    return response


def _emitted_ids(selector: RecordSelector, bases: list[Mapping[str, Any]]) -> list[str]:
    records = selector.select_records(response=_response(bases), stream_state={}, records_schema={})
    return [record.data["id"] for record in records]


def test_bases_filter_rejects_missing_null_and_empty_permission_level(bases_record_selector: RecordSelector) -> None:
    bases = [
        {"id": "appMissing", "name": "missing key"},
        {"id": "appNull", "name": "null value", "permissionLevel": None},
        {"id": "appEmpty", "name": "empty string", "permissionLevel": ""},
        {"id": "appCreate", "name": "valid", "permissionLevel": "create"},
    ]

    assert _emitted_ids(bases_record_selector, bases) == ["appCreate"]


@pytest.mark.parametrize("permission_level", [pytest.param(level, id=level) for level in VALID_PERMISSION_LEVELS])
def test_bases_filter_keeps_valid_permission_levels(bases_record_selector: RecordSelector, permission_level: str) -> None:
    bases = [{"id": "appValid", "name": "valid", "permissionLevel": permission_level}]

    assert _emitted_ids(bases_record_selector, bases) == ["appValid"]
