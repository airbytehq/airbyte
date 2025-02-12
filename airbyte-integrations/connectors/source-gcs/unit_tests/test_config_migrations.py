# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import pathlib
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from source_gcs import SourceGCS
from source_gcs.config_migrations import MigrateServiceAccount

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
        (str(pathlib.Path(__file__).parent / "resource/config_migrations/service_account_config.json"), True),
        # New config format
        (str(pathlib.Path(__file__).parent / "resource/config_migrations/service_account_with_credentials_config.json"), False),
    ],
)
def test_migrate_config(config_file_path, run_revert):
    args = ["check", "--config", config_file_path]
    source = SourceGCS(
        MagicMock(),
        MagicMock,
        None,
        AirbyteEntrypoint.extract_config(args),
        None,
    )

    MigrateServiceAccount().migrate(args, source)
    migrated_config = load_config(config_file_path)

    assert "credentials" in migrated_config
    assert "service_account" in migrated_config["credentials"]
    assert migrated_config["credentials"]["auth_type"] == "Service"

    if run_revert:
        revert_config(config_file_path)
