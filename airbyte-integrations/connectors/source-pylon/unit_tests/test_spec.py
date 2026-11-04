# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator


@pytest.mark.parametrize(
    "workers,valid", [(None, True), (1, True), (3, True), (10, True), (0, False), (11, False), (1.5, False), ("3", False)]
)
def test_optional_worker_bounds(manifest_path: Path, workers: int | float | str | None, valid: bool) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["spec"]["connection_specification"]
    config = {"api_token": "synthetic-token"}
    if workers is not None:
        config["num_workers"] = workers
    assert Draft7Validator(schema).is_valid(config) is valid
    assert schema["properties"]["num_workers"]["default"] == 3
