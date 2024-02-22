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


class MigrateAccessTokenToCredentials:
    """
    Facilitates the migration of configuration at runtime.
    This migration maintains backward compatibility with the previous version by creating a new property.
    When reverting to the previous source version, the connector will use the old property `access_token`.

    Starting from version `0.3.0`, the `access_token` property is relocated to the `credentials` property.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_from_key: str = "access_token"
    migrate_to_key: str = "credentials"
    default_values: dict = {"auth_method": "oauth2.0"}

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        Determines whether the configuration should be migrated to adopt the new structure for the `custom_reports`,
        based on the source specification.
        """
        return cls.migrate_to_key not in config

    @classmethod
    def transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Transforms the configuration."""
        migrated_config = {cls.migrate_to_key: {cls.migrate_from_key: config.get(cls.migrate_from_key), **cls.default_values}}
        return config | migrated_config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Modifies and saves the configuration."""
        migrated_config = cls.transform(config)
        source.write_config(migrated_config, config_path)
        return migrated_config

    @classmethod
    def obscure_access_token(cls, access_token: str) -> str:
        """Obscures the access token."""
        return "*" * (len(access_token) // 2)

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        """Emits the control message."""
        hashed_access_token = cls.obscure_access_token(migrated_config[cls.migrate_to_key][cls.migrate_from_key])
        hashed_config = migrated_config.copy()
        hashed_config[cls.migrate_to_key][cls.migrate_from_key] = hashed_access_token
        hashed_config[cls.migrate_from_key] = hashed_access_token

        control_message = create_connector_config_control_message(hashed_config)
        cls.message_repository.emit_message(control_message)
        for message in cls.message_repository._message_queue:
            print(message.json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        """
        Checks the input arguments, migrates the configuration if necessary, and emits the CONTROL message.
        """
        config_path = AirbyteEntrypoint(source).extract_config(args)
        if config_path:
            config = source.read_config(config_path)
            if cls.should_migrate(config):
                cls.emit_control_message(cls.modify_and_save(config_path, source, config))
