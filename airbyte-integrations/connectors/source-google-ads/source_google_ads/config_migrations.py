#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping

from airbyte_cdk.config_observation import create_connector_config_control_message, emit_configuration_as_airbyte_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.utils import AirbyteTracedException

from .utils import GAQL


FULL_REFRESH_CUSTOM_TABLE = [
    "asset",
    "asset_group_listing_group_filter",
    "custom_audience",
    "geo_target_constant",
    "change_event",
    "change_status",
]


class MigrateCustomQuery:
    """
    This class stands for migrating the config at runtime.
    This migration is backwards compatible with the previous version, as new property will be created.
    When falling back to the previous source version connector will use old property `custom_queries`.

    Add `segments.date` for all queries where it was previously added by IncrementalCustomQuery class.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        Determines if a configuration requires migration.

        Args:
        - config (Mapping[str, Any]): The configuration data to check.

        Returns:
        - True: If the configuration requires migration.
        - False: Otherwise.
        """
        return "custom_queries_array" not in config

    @classmethod
    def update_custom_queries(cls, config: Mapping[str, Any], source: Source = None) -> Mapping[str, Any]:
        """
        Update custom queries with segments.date field.

        Args:
        - config (Mapping[str, Any]): The configuration from which the key should be removed.
        - source (Source, optional): The data source. Defaults to None.

        Returns:
        - Mapping[str, Any]: The configuration after removing the key.
        """
        custom_queries = []
        for query in config.get("custom_queries", []):
            new_query = query.copy()
            try:
                query_object = GAQL.parse(query["query"])
            except ValueError:
                message = f"The custom GAQL query {query['table_name']} failed. Validate your GAQL query with the Google Ads query validator. https://developers.google.com/google-ads/api/fields/v13/query_validator"
                raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

            if query_object.resource_name not in FULL_REFRESH_CUSTOM_TABLE and "segments.date" not in query_object.fields:
                query_object = query_object.append_field("segments.date")

            new_query["query"] = str(query_object)
            custom_queries.append(new_query)

        config["custom_queries_array"] = custom_queries
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Modifies the configuration and then saves it back to the source.

        Args:
        - config_path (str): The path where the configuration is stored.
        - source (Source): The data source.
        - config (Mapping[str, Any]): The current configuration.

        Returns:
        - Mapping[str, Any]: The updated configuration.
        """
        migrated_config = cls.update_custom_queries(config, source)
        source.write_config(migrated_config, config_path)
        return migrated_config

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        """
        Orchestrates the configuration migration process.

        It first checks if the `--config` argument is provided, and if so,
        determines whether migration is needed, and then performs the migration
        if required.

        Args:
        - args (List[str]): List of command-line arguments.
        - source (Source): The data source.
        """
        config_path = AirbyteEntrypoint(source).extract_config(args)
        if config_path:
            config = source.read_config(config_path)
            if cls.should_migrate(config):
                emit_configuration_as_airbyte_control_message(cls.modify_and_save(config_path, source, config))
