#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from typing import Any, List, Mapping

from airbyte_cdk import AirbyteEntrypoint, Source, create_connector_config_control_message
from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message


logger = logging.getLogger("airbyte_logger")


class MigrateCredentials(ABC):
    """
    This class stands for migrating the config inside object `credentials`
    """

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        return "credentials" not in config

    @classmethod
    def migrate_config(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config["credentials"] = {
            "auth_method": "access_token",
            "access_token": config.pop("access_token"),
        }
        return config

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
        print(create_connector_config_control_message(migrated_config))

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
                emit_configuration_as_airbyte_control_message(cls.modify_and_save(config_path, source, config))
