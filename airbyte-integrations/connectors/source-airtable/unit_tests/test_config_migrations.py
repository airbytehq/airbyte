# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import pathlib
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from source_airtable import SourceAirtable
from source_airtable.config_migrations import MigrateApiKey

from airbyte_cdk import AirbyteEntrypoint


def load_config(path: str) -> Mapping[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def revert_config(path: str) -> None:
    migrated_config = load_config(path)
    del migrated_config["credentials"]
    with open(path, "w") as f:
        f.write(json.dumps(migrated_config))


@pytest.mark.parametrize(
    "config_file_path, run_revert",
    [
        # Migration is required
        (str(pathlib.Path(__file__).parent / "resources/configs/old.json"), True),
        # New config format
        (str(pathlib.Path(__file__).parent / "resources/configs/new.json"), False),
    ],
)
def test_config_migrations(config_file_path, run_revert):
    args = ["check", "--config", config_file_path]
    source = SourceAirtable(
        catalog=MagicMock(),
        config=AirbyteEntrypoint.extract_config(args),
        state=MagicMock(),
    )

    MigrateApiKey().migrate(args, source)
    migrated_config = load_config(config_file_path)

    assert "credentials" in migrated_config
    assert "api_key" in migrated_config["credentials"]
    assert migrated_config["credentials"]["auth_method"] == "api_key"

    if run_revert:
        revert_config(config_file_path)
