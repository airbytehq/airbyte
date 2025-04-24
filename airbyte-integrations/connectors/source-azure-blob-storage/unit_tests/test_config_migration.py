# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import json
import os
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Any, Mapping

from pytest import fixture
from source_azure_blob_storage import SourceAzureBlobStorage, SourceAzureBlobStorageSpec, SourceAzureBlobStorageStreamReader
from source_azure_blob_storage.config_migrations import MigrateCredentials, MigrateLegacyConfig

from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor


@fixture
def temp_configs():
    config_path = f"{os.path.dirname(__file__)}/test_configs/"
    with TemporaryDirectory() as _tempdir:
        configs_dir = Path(_tempdir) / "test_configs"
        copytree(config_path, configs_dir)
        yield configs_dir


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def test_legacy_config_migration(temp_configs):
    config_path = str((Path(temp_configs) / "test_legacy_config.json").resolve())
    migration_instance = MigrateLegacyConfig
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=SourceAzureBlobStorageSpec,
        catalog={},
        config=load_config(config_path),
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    migration_instance.migrate(["check", "--config", config_path], source)
    test_migrated_config = load_config(config_path)
    expected_config = {
        "azure_blob_storage_account_key": "secret/key==",
        "azure_blob_storage_account_name": "airbyteteststorage",
        "azure_blob_storage_container_name": "airbyte-source-azure-blob-storage-test",
        "azure_blob_storage_endpoint": "https://airbyteteststorage.blob.core.windows.net",
        "streams": [
            {
                "format": {"filetype": "jsonl"},
                "legacy_prefix": "subfolder/",
                "name": "airbyte-source-azure-blob-storage-test",
                "validation_policy": "Emit Record",
            }
        ],
    }
    assert test_migrated_config == expected_config


def test_credentials_config_migration(temp_configs):
    config_path = str((Path(temp_configs) / "test_config_without_credentials.json").resolve())
    initial_config = load_config(config_path)
    expected = initial_config["azure_blob_storage_account_key"]

    migration_instance = MigrateCredentials
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=SourceAzureBlobStorageSpec,
        catalog={},
        config=load_config(config_path),
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    migration_instance.migrate(["check", "--config", config_path], source)
    test_migrated_config = load_config(config_path)
    assert test_migrated_config["credentials"]["azure_blob_storage_account_key"] == expected
