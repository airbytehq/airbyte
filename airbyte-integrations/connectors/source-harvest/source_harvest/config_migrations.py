#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

logger = logging.getLogger("airbyte_logger")


class MigrateAuthType:
    """
    This class stands for migrating the config at runtime.
    This migration is backwards compatible with the previous version, as new `auth_type` property will be created and populated.
    When falling back to the previous source version connector will not require the `auth_type` field.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        Determines if a configuration requires migration.

        Args:
        - config (Mapping[str, Any]): The configuration data to check.

        Returns:
        - True: If the configuration requires migration (i.e. "auth_type" does not exist in the credentials being read).
        - False: Otherwise.
        """
        return "auth_type" not in config["credentials"]

    @classmethod
    def set_auth_type(cls, config: Mapping[str, Any], source: Source = None) -> Mapping[str, Any]:
        """
        Sets `auth_type` to "Token" if api_token exists in the credentials, sets it to "Client" for when client_id exists. Otherwise does not set `auth_type` as user has not provided any credentials.

        Args:
        - config (Mapping[str, Any]): The configuration from which the `auth_type` should be added and set.
        - source (Source, optional): The data source. Defaults to None.

        Returns:
        - Mapping[str, Any]: The configuration after removing the key.
        """
        if "api_token" in config["credentials"]:
            config["credentials"]["auth_type"] = "Token"
        elif "client_id" in config["credentials"]:
            config["credentials"]["auth_type"] = "Client"
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
        migrated_config = cls.set_auth_type(config, source)
        source.write_config(migrated_config, config_path)
        return migrated_config

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        """
        Emits the control messages related to configuration migration.

        Args:
        - migrated_config (Mapping[str, Any]): The migrated configuration.
        """
        cls.message_repository.emit_message(create_connector_config_control_message(migrated_config))
        for message in cls.message_repository._message_queue:
            print(message.json(exclude_unset=True))

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
