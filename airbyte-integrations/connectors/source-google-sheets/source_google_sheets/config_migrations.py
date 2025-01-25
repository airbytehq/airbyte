# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, List, Mapping

import dpath
import orjson

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteMessageSerializer
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from source_google_sheets import SourceGoogleSheets


class MigrateServiceAccountInfo:
    """
    Migrates service_account_info to a dict format.
    old:
    {
    "credentials": {"service_account_info": "{ \"some_key\": \"key\" }"
    }
    new:
    {
    "credentials": {"service_account": {"some_key": "key"}, "service_account_info": "{ \"some_key\": \"key\" }}
    }
    """

    migrate_from_path = ["credentials", "service_account_info"]
    migrate_to_path = ["credentials", "service_account"]

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        service_account_info = dpath.get(config, cls.migrate_from_path, default={})
        if service_account_info and isinstance(service_account_info, str):
            return True
        return False

    @classmethod
    def _migrate_service_account(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        service_account = json.loads(config["credentials"]["service_account_info"])
        dpath.new(config, cls.migrate_to_path, service_account)
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceGoogleSheets, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._migrate_service_account(config)
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
    def migrate(cls, args: List[str], source: SourceGoogleSheets) -> None:
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
