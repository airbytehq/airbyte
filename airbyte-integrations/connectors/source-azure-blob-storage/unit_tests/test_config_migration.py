# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import os
from typing import Any, Mapping

from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from source_azure_blob_storage import Config, SourceAzureBlobStorage, SourceAzureBlobStorageStreamReader
from source_azure_blob_storage.config_migrations import MigrateCredentials


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def test_mailchimp_config_migration():
    config_path = f"{os.path.dirname(__file__)}/test_configs/test_config_without_credentials.json"
    initial_config = load_config(config_path)
    migration_instance = MigrateCredentials
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=Config,
        catalog={},
        config=load_config(config_path),
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    migration_instance.migrate(["check", "--config", config_path], source)
    test_migrated_config = load_config(config_path)
    assert test_migrated_config["credentials"]["azure_blob_storage_account_key"] == initial_config["azure_blob_storage_account_key"]
