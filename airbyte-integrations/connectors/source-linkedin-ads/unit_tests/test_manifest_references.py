#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import yaml

from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _resolved_definitions() -> dict:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    return resolved["definitions"]


def test_manifest_has_no_yaml_anchors_or_aliases():
    manifest_text = _MANIFEST_PATH.read_text()
    anchor_or_alias_tokens = [token for token in yaml.scan(manifest_text) if isinstance(token, (yaml.AnchorToken, yaml.AliasToken))]
    assert not anchor_or_alias_tokens, (
        "manifest.yaml should not use YAML anchors or aliases; use declarative $ref instead. Found: "
        + ", ".join(f"{type(t).__name__}({t.value}) at line {t.start_mark.line + 1}" for t in anchor_or_alias_tokens)
    )


def test_impression_device_property_list_resolves_to_shared_list():
    definitions = _resolved_definitions()

    impression_device_properties = definitions["impression_device_analytics_query_properties"]["property_list"]
    shared_properties = definitions["analytics_query_properties"]["property_list"]

    assert impression_device_properties == shared_properties
    assert isinstance(impression_device_properties, list)
    assert len(impression_device_properties) == 95
    assert all(isinstance(prop, str) for prop in impression_device_properties)
    assert impression_device_properties[0] == "actionClicks"
    assert impression_device_properties[-1] == "viralVideoViews"
    assert "dateRange" in impression_device_properties
    assert "pivotValues" in impression_device_properties

    merge_strategy_keys = {
        name: definitions[name]["property_chunking"]["record_merge_strategy"]["key"]
        for name in ("analytics_query_properties", "impression_device_analytics_query_properties")
    }
    assert merge_strategy_keys["analytics_query_properties"] == ["end_date", "string_of_pivot_values"]
    assert merge_strategy_keys["impression_device_analytics_query_properties"] == [
        "end_date",
        "string_of_pivot_values",
        "sponsoredCampaign",
    ]


def test_impression_device_stream_query_properties_match_shared_list():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)

    def _stream_request_parameters(stream_name: str) -> dict:
        stream = next(s for s in resolved["streams"] if s["name"] == stream_name)
        return stream["retriever"]["requester"]["request_parameters"]

    impression_device_fields = _stream_request_parameters("ad_impression_device_analytics")["fields"]
    campaign_fields = _stream_request_parameters("ad_campaign_analytics")["fields"]

    assert impression_device_fields["type"] == "QueryProperties"
    assert impression_device_fields["property_list"] == campaign_fields["property_list"]
    assert impression_device_fields["property_list"] == resolved["definitions"]["analytics_query_properties"]["property_list"]
