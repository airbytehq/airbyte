# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository


class MigrateServiceAccount:
    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_from_path = "service_account"
    migrate_to_path = "credentials"

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        return config.get(cls.migrate_from_path) and not config.get(cls.migrate_to_path)

    @classmethod
    def transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config[cls.migrate_to_path] = {"service_account": config[cls.migrate_from_path], "auth_type": "Service"}
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        migrated_config = cls.transform(config)

        source.write_config(migrated_config, config_path)

        return migrated_config

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        # add the Airbyte Control Message to message repo
        cls.message_repository.emit_message(create_connector_config_control_message(migrated_config))
        # emit the Airbyte Control Message from message queue to stdout
        for message in cls.message_repository._message_queue:
            print(message)

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        """
        This method checks the input args, should the config be migrated,
        transform if necessary and emit the CONTROL message.
        """
        # get config path
        config_path = AirbyteEntrypoint(source).extract_config(args)
        # proceed only if `--config` arg is provided
        if config_path:
            # read the existing config
            config = source.read_config(config_path)
            # migration check
            if cls.should_migrate(config):
                cls.emit_control_message(
                    cls.modify_and_save(config_path, source, config),
                )
