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


class MigrateProjectId:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.
    Specifically, starting from `1.0.0`, the property `project_id` should be inside credentials block as it is only used for Service Account
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines if the config should be migrated to have the new path for project_id, based on the source spec.
        Returns:
            > True, if the transformation is neccessary
            > False, otherwise.
        """
        return "project_id" in config

    @classmethod
    def move_project_id(cls, config: Mapping[str, Any], source: Source = None) -> Mapping[str, Any]:
        # assign old values to new property that will be used within the new version
        if isinstance(config.get("credentials")):
            config["credentials"]["project_id"] = config["project_id"]
        else:
            config["credentials"] = {"project_id": config["project_id"]}
        config.pop("project_id")
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.move_project_id(config, source)
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
        transform if neccessary and emit the CONTROL message.
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
