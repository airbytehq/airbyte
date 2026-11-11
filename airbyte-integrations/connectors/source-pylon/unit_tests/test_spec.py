# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator

from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


@pytest.mark.parametrize(
    "workers,valid", [(None, True), (1, False), (2, True), (3, True), (10, True), (0, False), (11, False), (1.5, False), ("3", False)]
)
def test_optional_worker_bounds(manifest_path: Path, workers: int | float | str | None, valid: bool) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["spec"]["connection_specification"]
    config = {"api_token": "synthetic-token"}
    if workers is not None:
        config["num_workers"] = workers
    assert Draft7Validator(schema).is_valid(config) is valid
    assert schema["properties"]["num_workers"]["default"] == 3


@pytest.mark.parametrize("region,valid", [(None, True), ("us", True), ("eu", True), ("other", False), (1, False)])
def test_optional_region(manifest_path: Path, region: str | int | None, valid: bool) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["spec"]["connection_specification"]
    config = {"api_token": "synthetic-token"}
    if region is not None:
        config["region"] = region
    assert Draft7Validator(schema).is_valid(config) is valid
    assert schema["properties"]["region"]["enum"] == ["us", "eu"]
    assert schema["properties"]["region"]["default"] == "us"
    assert [schema["properties"][name]["order"] for name in ("api_token", "region", "start_date", "num_workers")] == [0, 1, 2, 3]


@pytest.mark.parametrize("region", ["us", "eu", "unexpected", None])
def test_requester_region_fallback(manifest_path: Path, region: str | None) -> None:
    manifest = yaml.safe_load(manifest_path.read_text())
    requester = ModelToComponentFactory().create_component(
        model_type=models.HttpRequester,
        component_definition=manifest["definitions"]["base_requester"],
        config={"api_token": "synthetic-token", "region": region},
        name="synthetic-region-test",
    )
    expected = "https://api.eu.usepylon.com" if region == "eu" else "https://api.usepylon.com"
    assert requester.get_url_base() == expected
