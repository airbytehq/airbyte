# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, List, Mapping

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from source_slack import SourceSlack


logger = logging.getLogger("airbyte_logger")


class MigrateLegacyConfig:
    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        legacy config:
        {
            "start_date": "2021-07-22T20:00:00Z",
            "end_date": "2021-07-23T20:00:00Z",
            "lookback_window": 1,
            "join_channels": True,
            "channel_filter": ["airbyte-for-beginners", "good-reads"],
            "api_token": "api-token"
        }
        api token should be in  the credentials object
        """
        if config.get("api_token") and not config.get("credentials"):
            return True
        return False

    @classmethod
    def _move_token_to_credentials(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        api_token = config["api_token"]
        config.update({"credentials": {"api_token": api_token, "option_title": "API Token Credentials"}})
        config.pop("api_token")
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceSlack, config: Mapping[str, Any]) -> Mapping[str, Any]:
        migrated_config = cls._move_token_to_credentials(config)
        # save the config
        source.write_config(migrated_config, config_path)
        return migrated_config

    @classmethod
    def _emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        # add the Airbyte Control Message to message repo
        cls.message_repository.emit_message(create_connector_config_control_message(migrated_config))
        # emit the Airbyte Control Message from message queue to stdout
        for message in cls.message_repository._message_queue:
            print(message.json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: SourceSlack) -> None:
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
