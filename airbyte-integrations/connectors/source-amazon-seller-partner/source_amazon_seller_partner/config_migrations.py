#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

from .source import SourceAmazonSellerPartner

logger = logging.getLogger("airbyte_logger")


class MigrateAccountType:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `2.0.1`, the `account_type` property becomes required.
    For those connector configs that do not contain this key, the default value of `Seller` will be used.
    Reverse operation is not needed as this field is ignored in previous versions of the connector.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migration_key: str = "account_type"

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether config requires migration.
        Returns:
            > True, if the transformation is neccessary
            > False, otherwise.
        """
        return cls.migration_key not in config

    @classmethod
    def _populate_with_default_value(cls, config: Mapping[str, Any], source: SourceAmazonSellerPartner = None) -> Mapping[str, Any]:
        config[cls.migration_key] = "Seller"
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceAmazonSellerPartner, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._populate_with_default_value(config, source)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

    @classmethod
    def _emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        # add the Airbyte Control Message to message repo
        cls.message_repository.emit_message(create_connector_config_control_message(migrated_config))
        # emit the Airbyte Control Message from message queue to stdout
        for message in cls.message_repository.consume_queue():
            print(message.json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: SourceAmazonSellerPartner) -> None:
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
            if cls._should_migrate(config):
                cls._emit_control_message(
                    cls._modify_and_save(config_path, source, config),
                )
