#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractmethod
from typing import Any, List, Mapping

from airbyte_cdk import AirbyteEntrypoint, Source, create_connector_config_control_message


logger = logging.getLogger("airbyte_logger")


class MigrateConfig(ABC):
    @classmethod
    @abstractmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool: ...

    @classmethod
    @abstractmethod
    def migrate_config(cls, config: Mapping[str, Any]) -> Mapping[str, Any]: ...

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Modifies the configuration and then saves it back to the source.

        Args:
        - config_path (str): The path where the configuration is stored.
        - source (Source): The data source.
        - config (Mapping[str, Any]): The current configuration.

        Returns:
        - Mapping[str, Any]: The updated configuration.
        """
        migrated_config = cls.migrate_config(config)
        source.write_config(migrated_config, config_path)
        return migrated_config

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        """
        Emits the control messages related to configuration migration.

        Args:
        - migrated_config (Mapping[str, Any]): The migrated configuration.
        """
        print(create_connector_config_control_message(migrated_config).json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        """
        Orchestrates the configuration migration process.

        It first checks if the `--config` argument is provided, and if so,
        determines whether migration is needed, and then performs the migration
        if required.

        Args:
        - args (List[str]): List of command-line arguments.
        - source (Source): The data source.
        """
        config_path = AirbyteEntrypoint(source).extract_config(args)
        if config_path:
            config = source.read_config(config_path)
            if cls.should_migrate(config):
                cls.emit_control_message(cls.modify_and_save(config_path, source, config))


class MigrateLegacyConfig(MigrateConfig):
    """
    Class that takes in Azure Blob Storage source configs in the legacy format and transforms them into
    configs that can be used by the new Azure Blob Storage source built with the file-based CDK.
    """

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        return "streams" not in config

    @classmethod
    def migrate_config(cls, legacy_config: Mapping[str, Any]) -> Mapping[str, Any]:
        azure_blob_storage_blobs_prefix = legacy_config.get("azure_blob_storage_blobs_prefix", "")
        return {
            "azure_blob_storage_endpoint": legacy_config.get("azure_blob_storage_endpoint", None),
            "azure_blob_storage_account_name": legacy_config["azure_blob_storage_account_name"],
            "azure_blob_storage_account_key": legacy_config["azure_blob_storage_account_key"],
            "azure_blob_storage_container_name": legacy_config["azure_blob_storage_container_name"],
            "streams": [
                {
                    "name": legacy_config["azure_blob_storage_container_name"],
                    "legacy_prefix": azure_blob_storage_blobs_prefix,
                    "validation_policy": "Emit Record",
                    "format": {"filetype": "jsonl"},
                }
            ],
        }


class MigrateCredentials(MigrateConfig):
    """
    This class stands for migrating the config azure_blob_storage_account_key inside object `credentials`
    """

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        return "credentials" not in config

    @classmethod
    def migrate_config(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config["credentials"] = {
            "auth_type": "storage_account_key",
            "azure_blob_storage_account_key": config.pop("azure_blob_storage_account_key"),
        }
        return config
