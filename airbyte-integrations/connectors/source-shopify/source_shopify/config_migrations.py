#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteMessageSerializer
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from orjson import orjson


class MigrateConfig:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `2.0.1`, the `start_date` property should be not (None or `None`):
        > "start_date": "2020-01-01"
    instead of, in `2.0.0` for some older configs, when the `start_date` was not required:
        > {...}
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_key: str = "start_date"
    # default spec value for the `start_date` is `2020-01-01`
    default_start_date_value: str = "2020-01-01"

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to have the new structure with `start_date`,
        based on the source spec.

        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        # If the config was already migrated, there is no need to do this again.
        # but if the customer has already switched to the new version,
        # corrected the old config and switches back to the new version,
        # we should try to migrate the modified old custom reports.
        none_values: List[str] = [None, "None"]
        key_not_present_in_config = cls.migrate_key not in config
        key_present_in_config_but_invalid = cls.migrate_key in config and config.get(cls.migrate_key) in none_values

        if key_not_present_in_config:
            return True
        elif key_present_in_config_but_invalid:
            return True
        else:
            return False

    @classmethod
    def modify_config(cls, config: Mapping[str, Any], source: Source = None) -> Mapping[str, Any]:
        config[cls.migrate_key] = cls.default_start_date_value
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.modify_config(config, source)
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
            print(orjson.dumps(AirbyteMessageSerializer.dump(message)).decode())

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
