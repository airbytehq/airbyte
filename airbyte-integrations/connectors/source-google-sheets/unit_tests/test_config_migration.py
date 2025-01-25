#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import pathlib
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from source_google_sheets import SourceGoogleSheets
from source_google_sheets.config_migrations import MigrateServiceAccountInfo

from airbyte_cdk import AirbyteEntrypoint


def load_config(path: str) -> Mapping[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def revert_config(path: str) -> None:
    migrated_config = load_config(path)

    del migrated_config["credentials"]["service_account"]
    with open(path, "w") as f:
        f.write(json.dumps(migrated_config))


@pytest.mark.parametrize(
    "config_file_path, run_revert",
    [
        (str(pathlib.Path(__file__).parent / "config_migration/old_config.json"), True),
        (str(pathlib.Path(__file__).parent / "config_migration/new_config.json"), False),
    ],
)
def test_config_migrations(config_file_path, run_revert):
    args = ["check", "--config", config_file_path]
    source = SourceGoogleSheets(
        catalog=MagicMock(),
        config=AirbyteEntrypoint.extract_config(args),
        state=MagicMock(),
    )

    MigrateServiceAccountInfo().migrate(args, source)
    migrated_config = load_config(config_file_path)

    assert "service_account" in migrated_config["credentials"]
    assert "service_account_info" in migrated_config["credentials"]
    assert isinstance(migrated_config["credentials"]["service_account"], dict)

    if run_revert:
        revert_config(config_file_path)
