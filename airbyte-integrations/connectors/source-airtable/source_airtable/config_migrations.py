# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping

import orjson

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteMessageSerializer
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from source_airtable import SourceAirtable


class MigrateApiKey:
    """
    Migrates old configs to a new supported format.

    OLD:
    {
    "api_key": ...
    }

    NEW:
    {
    "credentials": {"api_key": ..., "auth_method": "api_key"}
    }

    """

    migrate_from_key = "api_key"
    migrate_to_key = "credentials"

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        if cls.migrate_from_key in config and cls.migrate_to_key not in config:
            return True
        return False

    @classmethod
    def _migrate_api_key(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config[cls.migrate_to_key] = {cls.migrate_from_key: config[cls.migrate_from_key], "auth_method": "api_key"}
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceAirtable, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._migrate_api_key(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

    @classmethod
    def _emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        # add the Airbyte Control Message to message repo
        cls.message_repository.emit_message(create_connector_config_control_message(migrated_config))
        # emit the Airbyte Control Message from message queue to stdout
        for message in cls.message_repository._message_queue:
            print(orjson.dumps(AirbyteMessageSerializer.dump(message)).decode())

    @classmethod
    def migrate(cls, args: List[str], source: SourceAirtable) -> None:
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
            if cls._should_migrate(config):
                cls._emit_control_message(
                    cls._modify_and_save(config_path, source, config),
                )
