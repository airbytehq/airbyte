#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import urllib.parse
from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository


logger = logging.getLogger("airbyte")


class JinaAiReaderConfigMigration:
    """
    This class stands for migrating the search prompt config at runtime to encode characters.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        based on the source spec.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
            > Raises the Exception if the structure could not be migrated.
        """
        return cls.is_url_encoded(config["search_prompt"])  # if search_prompt given in config is not encoded

    @classmethod
    def is_url_encoded(cls, s: str) -> bool:
        return s == urllib.parse.unquote(s)

    @classmethod
    def modify(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if "search_prompt" in config:
            if cls.is_url_encoded(config["search_prompt"]):
                config["search_prompt"] = urllib.parse.quote(config["search_prompt"])
            else:
                raise ValueError(f"Invalid config. got {config}")
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.modify(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        # add the Airbyte Control Message to message repo
        cls.message_repository.emit_message(create_connector_config_control_message(migrated_config))
        # emit the Airbyte Control Message from message queue to stdout
        for message in cls.message_repository._message_queue:
            print(message.json(exclude_unset=True))

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
