#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import abc
import logging
from abc import ABC
from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

from .source import SourceGithub


logger = logging.getLogger("airbyte_logger")


class MigrateStringToArray(ABC):
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `1.4.6`, the `repository` and `branch` properties should be like :
        > List(["<repository_1>", "<repository_2>", ..., "<repository_n>"])
    instead of, in `1.4.5`:
        > JSON STR: "repository_1 repository_2"
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @property
    @abc.abstractmethod
    def migrate_from_key(self) -> str: ...

    @property
    @abc.abstractmethod
    def migrate_to_key(self) -> str: ...

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether config require migration.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        if cls.migrate_from_key in config and cls.migrate_to_key not in config:
            return True
        return False

    @classmethod
    def _transform_to_array(cls, config: Mapping[str, Any], source: SourceGithub = None) -> Mapping[str, Any]:
        # assign old values to new property that will be used within the new version
        config[cls.migrate_to_key] = config[cls.migrate_to_key] if cls.migrate_to_key in config else []
        data = set(filter(None, config.get(cls.migrate_from_key).split(" ")))
        config[cls.migrate_to_key] = list(data | set(config[cls.migrate_to_key]))
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceGithub, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._transform_to_array(config, source)
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
            print(message.json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: SourceGithub) -> None:
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


class MigrateRepository(MigrateStringToArray):
    migrate_from_key: str = "repository"
    migrate_to_key: str = "repositories"


class MigrateBranch(MigrateStringToArray):
    migrate_from_key: str = "branch"
    migrate_to_key: str = "branches"
