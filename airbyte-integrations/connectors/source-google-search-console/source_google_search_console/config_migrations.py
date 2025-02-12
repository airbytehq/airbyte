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


class MigrateCustomReports:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `1.3.3`, the `custom_reports` property should be like :
        > List([{name: my_report}, {dimensions: [a,b,c]}], [], ...)
    instead of, in `1.3.2`:
        > JSON STR: "{name: my_report}, {dimensions: [a,b,c]}"
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_from_key: str = "custom_reports"
    migrate_to_key: str = "custom_reports_array"

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to have the new structure for the `custom_reports`,
        based on the source spec.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
            > Raises the Exception if the structure could not be migrated.
        """
        # If the config was already migrated, there is no need to do this again.
        # but if the customer has already switched to the new version,
        # corrected the old config and switches back to the new version,
        # we should try to migrate the modified old custom reports.
        if cls.migrate_to_key in config:
            # also we need to make sure this is not a newly created connection
            return len(config[cls.migrate_to_key]) == 0 and cls.migrate_from_key in config

        if cls.migrate_from_key in config:
            custom_reports = config[cls.migrate_from_key]
            # check the old structure vs new spec
            if isinstance(custom_reports, str):
                return True
        return False

    @classmethod
    def transform_to_array(cls, config: Mapping[str, Any], source: Source = None) -> Mapping[str, Any]:
        # assign old values to new property that will be used within the new version
        config[cls.migrate_to_key] = config[cls.migrate_from_key]
        # transfom `json_str` to `list` of objects
        return source._validate_custom_reports(config)

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.transform_to_array(config, source)
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
