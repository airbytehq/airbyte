# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
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
        "default_concurrency": "{{ [config.get('num_workers') or 3, 2] | max }}",
        "max_concurrency": 10,
    }


@pytest.mark.parametrize(
    "num_workers, expected",
    [
        pytest.param(None, 3, id="absent"),
        pytest.param(1, 2, id="one_runs_as_two"),
        pytest.param(5, 5, id="five"),
    ],
)
def test_concurrency_never_drops_below_two(num_workers, expected):
    # The CDK's lowest safe concurrency is 2, and the spec still allows 1 for configs saved by 1.2.0.
    from airbyte_cdk.sources.declarative.concurrency_level import ConcurrencyLevel

    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    config = {} if num_workers is None else {"num_workers": num_workers}
    level = ConcurrencyLevel(
        default_concurrency=manifest["concurrency_level"]["default_concurrency"],
        max_concurrency=manifest["concurrency_level"]["max_concurrency"],
        config=config,
        parameters={},
    )
    assert level.get_concurrency_level() == expected
