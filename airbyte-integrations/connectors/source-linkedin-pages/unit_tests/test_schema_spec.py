# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import yaml
from conftest import MANIFEST_PATH


def test_organization_lookup_schema_covers_documented_locale_and_staff_range():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    stream = next(stream for stream in manifest["streams"] if stream["name"] == "organization_lookup")
    properties = stream["schema_loader"]["schema"]["properties"]

    assert properties["staffCountRange"]["type"] == ["string", "null"]
    localized = properties["name"]["properties"]["localized"]
    assert localized["properties"]["ru_RU"]["type"] == ["string", "null"]
    assert localized["additionalProperties"] == {"type": ["string", "null"]}


def test_spec_fields_and_concurrency():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    spec = manifest["spec"]["connection_specification"]
    properties = spec["properties"]

    assert spec["required"] == ["org_id"]
    assert properties["org_id"]["airbyte_secret"] is True
    assert "123456789" in properties["org_id"]["description"]
    assert "default" not in properties["start_date"]
    assert "bit.ly" not in properties["start_date"]["description"]
    assert "{{" not in properties["start_date"]["description"]
    assert properties["credentials"]["type"] == "object"
    num_workers = properties["num_workers"]
    assert num_workers["type"] == "integer"
    assert num_workers["title"] == "Number of concurrent workers"
    assert num_workers["minimum"] == 1
    assert num_workers["maximum"] == 10
    assert num_workers["default"] == 3
    assert num_workers["order"] == 4
    assert "per-application daily quota" in num_workers["description"]
    assert manifest["concurrency_level"] == {
        "type": "ConcurrencyLevel",
        "default_concurrency": "{{ config.get('num_workers', 3) }}",
        "max_concurrency": 10,
    }
