#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Dict, List, Mapping

from airbyte_cdk import emit_configuration_as_airbyte_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from source_facebook_marketing.spec import ValidAdSetStatuses, ValidAdStatuses, ValidCampaignStatuses


logger = logging.getLogger("airbyte_logger")


class MigrateAccountIdToArray:
    """
    This class stands for migrating the config at runtime.
    This migration is backwards compatible with the previous version, as new property will be created.
    When falling back to the previous source version connector will use old property `account_id`.

    Starting from `1.3.0`, the `account_id` property is replaced with `account_ids` property, which is a list of strings.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_from_key: str = "account_id"
    migrate_to_key: str = "account_ids"

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
        return cls.migrate_from_key in config and cls.migrate_to_key not in config

    @classmethod
    def transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # transform the config
        config[cls.migrate_to_key] = [config[cls.migrate_from_key]]
        # return transformed config
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.transform(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

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
                emit_configuration_as_airbyte_control_message(cls.modify_and_save(config_path, source, config))


class MigrateIncludeDeletedToStatusFilters(MigrateAccountIdToArray):
    """
    This class stands for migrating the config at runtime.
    This migration is backwards compatible with the previous version, as new property will be created.
    When falling back to the previous source version connector will use old property `include_deleted`.

    Starting from `1.4.0`, the `include_deleted` property is replaced with `ad_statuses`,
    `ad_statuses` and `campaign_statuses` which represent status filters.
    """

    migrate_from_key: str = "include_deleted"
    migrate_to_key: str = "ad_statuses"
    stream_filter_to_statuses: Mapping[str, List[str]] = {
        "ad_statuses": [status.value for status in ValidAdStatuses],
        "adset_statuses": [status.value for status in ValidAdSetStatuses],
        "campaign_statuses": [status.value for status in ValidCampaignStatuses],
    }

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to have the new property for filters.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
            > Raises the Exception if the structure could not be migrated.
        """
        config_is_updated = config.get(cls.migrate_to_key)
        no_include_deleted = not config.get(cls.migrate_from_key)
        return False if config_is_updated or no_include_deleted else True

    @classmethod
    def transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # transform the config
        for stream_filter, statuses in cls.stream_filter_to_statuses.items():
            config[stream_filter] = statuses
        # return transformed config
        return config


class MigrateSecretsPathInConnector:
    """
    This class stands for migrating the config at runtime.
    This migration is intended for backwards compatibility with the previous version, so existing secrets configurations gets migrated to new path.

    Starting from `2.2.0`, the `client_id`, `client_secret` and `access_token` will be placed at `credentials` path.
    """

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to nest existing fields at credentials.
        It is assumed if credentials does not exist on configuration, `client_id`, `client_secret` and `access_token` exists on root path.
        Returns:
            > True, if the migration is necessary
            > False, otherwise.
        """
        return "access_token" in config or "client_id" in config or "client_secret" in config

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
            if cls._should_migrate(config):
                emit_configuration_as_airbyte_control_message(cls._modify_and_save(config_path, source, config))

    @classmethod
    def _transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # transform the config
        if "credentials" not in config:
            config["credentials"] = {
                "auth_type": "Service",
            }
        if "access_token" in config:
            config["credentials"]["access_token"] = config.pop("access_token")
        if "client_id" in config:
            config["credentials"]["auth_type"] = "Client"
            config["credentials"]["client_id"] = config.pop("client_id")
        if "client_secret" in config:
            config["credentials"]["auth_type"] = "Client"
            config["credentials"]["client_secret"] = config.pop("client_secret")
        # return transformed config
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._transform(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config


class RemoveActionReportTimeMigration:
    """
    Runtime config migrator that **removes** the deprecated
    ``action_report_time`` property.

    The field was deprecated starting in version 3.5.0.
    """

    migrate_key: str = "action_report_time"

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """Return ``True`` when the deprecated key is present."""
        return any(cls.migrate_key in report for report in config.get("custom_insights", []))

    @classmethod
    def transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return a copy of *config* without the deprecated key.
        The original mapping is left untouched.
        """
        config_copy: Dict[str, Any] = dict(config)
        for report in config_copy["custom_insights"]:
            report.pop(cls.migrate_key, None)
        return config_copy

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls.transform(config)
        # save the config
        source.write_config(migrated_config, config_path)
        # return modified config
        return migrated_config

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        # get config path
        config_path = AirbyteEntrypoint(source).extract_config(args)
        # proceed only if `--config` arg is provided
        if config_path:
            # read the existing config
            config = source.read_config(config_path)
            # migration check
            if cls.should_migrate(config):
                emit_configuration_as_airbyte_control_message(cls.modify_and_save(config_path, source, config))
