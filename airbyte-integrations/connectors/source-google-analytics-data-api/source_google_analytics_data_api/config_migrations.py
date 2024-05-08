#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping

import dpath.util
from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository

from .source import SourceGoogleAnalyticsDataApi

logger = logging.getLogger("airbyte_logger")


class MigratePropertyID:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `1.3.0`, the `property_id` property should be like :
        > List(["<property_id 1>", "<property_id 2>", ..., "<property_id n>"])
    instead of, in `1.2.0`:
        > JSON STR: "<property_id>"
    """

    message_repository: MessageRepository = InMemoryMessageRepository()
    migrate_from_key: str = "property_id"
    migrate_to_key: str = "property_ids"

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether config requires migration.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """
        if cls.migrate_from_key in config:
            return True
        return False

    @classmethod
    def _transform_to_array(cls, config: Mapping[str, Any], source: SourceGoogleAnalyticsDataApi = None) -> Mapping[str, Any]:
        # assign old values to new property that will be used within the new version
        config[cls.migrate_to_key] = config[cls.migrate_to_key] if cls.migrate_to_key in config else []
        data = config.pop(cls.migrate_from_key)
        if data not in config[cls.migrate_to_key]:
            config[cls.migrate_to_key].append(data)
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceGoogleAnalyticsDataApi, config: Mapping[str, Any]) -> Mapping[str, Any]:
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
        for message in cls.message_repository.consume_queue():
            print(message.json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: SourceGoogleAnalyticsDataApi) -> None:
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
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to have the new structure for the `custom_reports`,
        based on the source spec.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
            > Raises the Exception if the structure could not be migrated.
        """

        # If the config has been migrated and has entries, no need to migrate again.
        if config.get(cls.migrate_to_key, []):
            return False

        # If the old config key is present and its value is a string, migration is needed.
        if config.get(cls.migrate_from_key, None) is not None and isinstance(config[cls.migrate_from_key], str):
            return True

        return False

    @classmethod
    def _transform_to_array(cls, config: Mapping[str, Any], source: SourceGoogleAnalyticsDataApi = None) -> Mapping[str, Any]:
        # assign old values to new property that will be used within the new version
        config[cls.migrate_to_key] = config[cls.migrate_from_key]
        # transform `json_str` to `list` of objects
        return source._validate_custom_reports(config)

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceGoogleAnalyticsDataApi, config: Mapping[str, Any]) -> Mapping[str, Any]:
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
        for message in cls.message_repository.consume_queue():
            print(message.json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: SourceGoogleAnalyticsDataApi) -> None:
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


class MigrateCustomReportsCohortSpec:
    """
    This class stands for migrating the config at runtime,
    Specifically, starting from `2.1.0`; the `cohortSpec` property will be added tp `custom_reports_array` with flag `enabled`:
        > List([{name: my_report, "cohortSpec": { "enabled": "true" } }, ...])
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def _should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines whether the config should be migrated to have the new structure for the `cohortSpec` inside `custom_reports`,
        based on the source spec.
        Returns:
            > True, if the transformation is necessary
            > False, otherwise.
        """

        return not dpath.util.search(config, "custom_reports_array/**/cohortSpec/enabled")

    @classmethod
    def _transform_custom_reports_cohort_spec(
        cls,
        config: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Assign `enabled` property that will be used within the new version"""
        for report in config.get("custom_reports_array", []):
            if report.get("cohortSpec"):
                report["cohortSpec"]["enabled"] = "true"
            else:
                report.setdefault("cohortSpec", {})["enabled"] = "false"
        return config

    @classmethod
    def _modify_and_save(cls, config_path: str, source: SourceGoogleAnalyticsDataApi, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # modify the config
        migrated_config = cls._transform_custom_reports_cohort_spec(config)
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
    def migrate(cls, args: List[str], source: SourceGoogleAnalyticsDataApi) -> None:
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
