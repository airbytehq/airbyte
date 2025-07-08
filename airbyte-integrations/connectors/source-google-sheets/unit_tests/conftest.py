#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path

import pytest

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


@pytest.fixture
def invalid_config():
    return {
        "spreadsheet_id": "invalid_spreadsheet_id",
        "credentials": {
            "auth_type": "Client",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "refresh_token": "fake_refresh_token",
        },
    }


@pytest.fixture
def catalog():
    def maker(*name_schema_pairs):
        for name, schema in name_schema_pairs:
            yield ConfiguredAirbyteStream(
                stream=AirbyteStream(name=name, json_schema=schema, supported_sync_modes=["full_refresh"]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )

    return maker
