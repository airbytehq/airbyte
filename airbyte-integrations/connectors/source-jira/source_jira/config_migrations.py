#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

logger = logging.getLogger("airbyte")


class MigrateIssueExpandProperties:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `0.6.1`, the `issues_stream_expand` property should be like :
        > List("renderedFields", "transitions", "changelog" ...)
    instead of, in `0.6.0`:
        > expand_issue_changelog: bool: True
        > render_fields: bool: True
        > expand_issue_transition: bool: True
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_from_keys_map: dict = {
        "expand_issue_changelog": "changelog",
        "render_fields": "renderedFields",
        "expand_issue_transition": "transitions",
    }
    migrate_to_key: str = "issues_stream_expand_with"

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to have the new structure for the `issues_stream_expand_with`,
        based on the source spec.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
            > Raises the Exception if the structure could not be migrated.
        """
        # If the config was already migrated, there is no need to do this again.
        # but if the customer has already switched to the new version,
        # corrected the old config and switches back to the new version,
        # we should try to migrate the modified old issue expand properties.
        if cls.migrate_to_key in config:
            return not len(config[cls.migrate_to_key]) > 0

        if any(config.get(key) for key in cls.migrate_from_keys_map):
            return True
        return False

    @classmethod
    def transform_to_array(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # assign old values to new property that will be used within the new version
        config[cls.migrate_to_key] = []
        for k, v in cls.migrate_from_keys_map.items():
            if config.get(k):
                config[cls.migrate_to_key].append(v)
        # transform boolean flags to `list` of objects
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.transform_to_array(config)
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
