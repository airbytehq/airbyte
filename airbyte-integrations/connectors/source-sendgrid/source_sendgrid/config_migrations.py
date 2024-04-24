#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional

import pendulum
from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

logger = logging.getLogger("airbyte_logger")


class MigrateToLowcodeConfig:
    """
    This class stands for migrating the config at runtime.
    Specifically, starting from `0.5.0`, apikey moved to api_key and start_time moved to start_date.
    start_time was not required and now start_date is.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines if the config should be migrated.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        has_api = "apikey" in config
        has_time = "start_time" in config
        has_new_api = "api_key" in config
        has_new_date = "start_date" in config
        if has_new_api and has_new_date:
            return False
        return has_api or has_time

    @staticmethod
    def transform_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        # move api_secret inside credentials block
        if "apikey" in config:
            config["api_key"] = config["apikey"]

        if "start_time" in config:
            epoch_time = parse_config_int(config["start_time"])
            if epoch_time:
                config["start_date"] = pendulum.from_timestamp(epoch_time, tz="UTC").to_iso8601_string()
            else:
                config["start_date"] = pendulum.parse(config["start_time"]).to_iso8601_string()

        if "start_date" not in config:
            config["start_date"] = "2009-08-01T00:00:00Z"

        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.transform_config(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        print(create_connector_config_control_message(migrated_config).json(exclude_unset=True))

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
                cls.emit_control_message(cls.modify_and_save(config_path, source, config))


def parse_config_int(value) -> Optional[int]:
    if isinstance(value, int):
        return value
    try:
        if float(value) == int(float(value)):
            return int(value)
    except (ValueError, TypeError):
        return None
    return None
