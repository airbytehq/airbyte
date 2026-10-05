# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Iterable, Mapping

import pytest
import yaml

from airbyte_cdk.sources.declarative.models.declarative_component_schema import DynamicSchemaLoader as DynamicSchemaLoaderModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


CONFIG = {"credentials": {"auth_method": "api_key", "api_key": "test-key"}}
LOOKUP_TYPES = ["lookup", "multipleLookupValues"]

# A table as returned by GET /v0/meta/bases/{baseId}/tables.
TABLE = {
    "id": "tblTest",
    "name": "Insertions",
    "fields": [
        {
            "id": "fldAiLookup",
            "name": "AI Lookup",
            "type": "multipleLookupValues",
            "options": {"isValid": True, "result": {"type": "aiText", "options": {}}},
        },
        {
            "id": "fldAiLegacyLookup",
            "name": "AI Legacy Lookup",
            "type": "lookup",
            "options": {"result": {"type": "aiText", "options": {}}},
        },
        {
            "id": "fldUnknownLookup",
            "name": "Unknown Lookup",
            "type": "multipleLookupValues",
            "options": {"isValid": True, "result": {"type": "someFutureFieldType"}},
        },
        {
            "id": "fldUnknownLegacyLookup",
            "name": "Unknown Legacy Lookup",
            "type": "lookup",
            "options": {"result": {"type": "someFutureFieldType"}},
        },
        {
            "id": "fldTextLookup",
            "name": "Text Lookup",
            "type": "multipleLookupValues",
            "options": {"isValid": True, "result": {"type": "singleLineText"}},
        },
        {
            "id": "fldNumberLookup",
            "name": "Number Lookup",
            "type": "multipleLookupValues",
            "options": {"isValid": True, "result": {"type": "number"}},
        },
        {"id": "fldAi", "name": "AI Summary", "type": "aiText", "options": {}},
        {"id": "fldName", "name": "Name", "type": "singleLineText"},
    ],
}


class _StubRetriever:
    """Replaces the schema loader's HTTP retriever (GET meta/bases/{baseId}/tables)."""

    def read_records(self, *args: Any, **kwargs: Any) -> Iterable[Mapping[str, Any]]:
        yield TABLE


def _types_mapping(manifest_path: Path) -> list:
    manifest = yaml.safe_load(manifest_path.read_text())
    schema_loader = manifest["definitions"]["streams"]["airtable_stream"]["schema_loader"]
    return schema_loader["schema_type_identifier"]["types_mapping"]


@pytest.fixture(scope="module")
def schema_properties(manifest_path: Path) -> Mapping[str, Any]:
    manifest = yaml.safe_load(manifest_path.read_text())
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    loader_definition = resolved["definitions"]["streams"]["airtable_stream"]["schema_loader"]
    loader_definition = ManifestComponentTransformer().propagate_types_and_parameters("", loader_definition, {})
    loader = ModelToComponentFactory().create_component(DynamicSchemaLoaderModel, loader_definition, CONFIG)
    loader.retriever = _StubRetriever()
    return loader.get_json_schema()["properties"]


@pytest.mark.parametrize("key", ["ai_lookup", "ai_legacy_lookup"])
def test_lookup_of_ai_text_is_an_array_of_objects(schema_properties: Mapping[str, Any], key: str) -> None:
    assert schema_properties[key] == {"type": ["null", "array"], "items": {"type": ["null", "object"]}}


@pytest.mark.parametrize("key", ["unknown_lookup", "unknown_legacy_lookup"])
def test_lookup_of_unmapped_type_falls_back_to_untyped_array(schema_properties: Mapping[str, Any], key: str) -> None:
    assert schema_properties[key] == {"type": ["null", "array"]}


def test_mapped_lookups_keep_their_item_types(schema_properties: Mapping[str, Any]) -> None:
    assert schema_properties["text_lookup"] == {"type": ["null", "array"], "items": {"type": ["null", "string"]}}
    assert schema_properties["number_lookup"] == {"type": ["null", "array"], "items": {"type": ["null", "number"]}}


def test_other_field_types_are_unchanged(schema_properties: Mapping[str, Any]) -> None:
    assert schema_properties["ai_summary"] == {"type": ["null", "string"]}
    assert schema_properties["name"] == {"type": ["null", "string"]}


@pytest.mark.parametrize("current_type", LOOKUP_TYPES)
def test_fallback_is_the_last_and_only_unconditional_rule(manifest_path: Path, current_type: str) -> None:
    """The first matching TypesMap wins, so a fallback placed earlier would shadow the typed rules."""
    rules = [rule for rule in _types_mapping(manifest_path) if rule["current_type"] == current_type]
    unconditional = [index for index, rule in enumerate(rules) if "condition" not in rule]
    assert unconditional == [len(rules) - 1]
    assert rules[-1]["target_type"] == "array"
