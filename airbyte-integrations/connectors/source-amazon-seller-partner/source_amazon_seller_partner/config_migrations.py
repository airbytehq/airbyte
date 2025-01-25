#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import abc
import json
import logging
from typing import Any, List, Mapping

from airbyte_cdk import emit_configuration_as_airbyte_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

from .source import SourceAmazonSellerPartner


logger = logging.getLogger("airbyte_logger")


class Migration:
    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    @abc.abstractmethod
    def _transform(cls, config: Mapping[str, Any]):
        pass

    @classmethod
    @abc.abstractmethod
    def _should_migrate(cls, config: Mapping[str, Any]):
        pass

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceAmazonSellerPartner, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._transform(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

    @classmethod
    def migrate(cls, args: List[str], source: SourceAmazonSellerPartner) -> None:
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
                emit_configuration_as_airbyte_control_message(cls._modify_and_save(config_path, source, config))


class MigrateAccountType(Migration):
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `2.0.1`, the `account_type` property becomes required.
    For those connector configs that do not contain this key, the default value of `Seller` will be used.
    Reverse operation is not needed as this field is ignored in previous versions of the connector.
    """

    migration_key: str = "account_type"

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether config requires migration.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        return cls.migration_key not in config

    @classmethod
    def _transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config[cls.migration_key] = "Seller"
        return config


class MigrateReportOptions(Migration):
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `2.0.1`, the `account_type` property becomes required.
    For those connector configs that do not contain this key, the default value of `Seller` will be used.
    Reverse operation is not needed as this field is ignored in previous versions of the connector.
    """

    migration_key: str = "report_options_list"

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether config requires migration.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        return cls.migration_key not in config and (config.get("report_options") or config.get("advanced_stream_options"))

    @classmethod
    def _transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            report_options = json.loads(config.get("report_options", "{}") or "{}")
        except json.JSONDecodeError:
            report_options = {}

        report_options_list = []
        for stream_name, options in report_options.items():
            options_list = [{"option_name": name, "option_value": value} for name, value in options.items()]
            report_options_list.append({"stream_name": stream_name, "options_list": options_list})

        config[cls.migration_key] = report_options_list
        return config


class MigrateStreamNameOption(Migration):
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `4.3.0`, the `report_options_list` property holds a list of objects,
    each of which now is required to have a `stream_name` property.
    For those connector configs that do not contain this key, the default value of <report_name> will be used.
    Reverse operation is not needed as this field is ignored in previous versions of the connector.
    """

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether config requires migration.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        if "report_options_list" not in config:
            return False

        options_list = config["report_options_list"]
        for options in options_list:
            if "report_name" not in options:
                return True
        return False

    @classmethod
    def _transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        report_options_list = []
        for report_options in config["report_options_list"]:
            if "report_name" not in report_options:
                report_options["report_name"] = report_options["stream_name"]
            report_options_list.append(report_options)

        config["report_options_list"] = report_options_list
        return config
