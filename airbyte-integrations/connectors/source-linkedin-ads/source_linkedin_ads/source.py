#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from copy import deepcopy
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException

from .utils import update_specific_key

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceLinkedinAds(YamlDeclarativeSource):
    def __init__(self):
        """
        Initializes the SourceLinkedinAds class with the path to the YAML manifest.
        """
        super().__init__(path_to_yaml="manifest.yaml")

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Assess the availability of the connector's connection.

        The customer must have the "r_liteprofile" scope enabled.
        More info: https://docs.microsoft.com/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin

        :param logger: Logger object to log the information.
        :param config: Configuration mapping containing necessary parameters.
        :return: A tuple containing a boolean indicating success or failure and an optional message or object.
        """
        self._validate_ad_analytics_reports(config)
        return super().check_connection(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Map the user input configuration as defined in the connector spec.
        Pass config to the streams.

        :param config: Configuration mapping containing necessary parameters.
        :return: List of streams.
        """
        self._validate_ad_analytics_reports(config)
        streams = super().streams(config=config)
        custom_ad_analytics_streams = self._create_custom_ad_analytics_streams(config)

        return streams + custom_ad_analytics_streams

    @staticmethod
    def _validate_ad_analytics_reports(config: Mapping[str, Any]) -> None:
        """
        Validates that the ad analytics reports in the config have unique names.

        :param config: Configuration mapping containing ad analytics reports.
        :raises AirbyteTracedException: If duplicate report names are found.
        """
        report_names = [x["name"] for x in config.get("ad_analytics_reports", [])]
        if len(report_names) != len(set(report_names)):
            duplicate_streams = {name for name in report_names if report_names.count(name) > 1}
            message = f"Stream names for Custom Ad Analytics reports should be unique, duplicated streams: {duplicate_streams}"
            raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

    def _create_custom_ad_analytics_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Create custom ad analytics streams based on the user configuration.

        :param config: Configuration mapping containing necessary parameters.
        :return: List of custom ad analytics streams.
        """
        stream_configs = self._stream_configs(self._source_config)
        custom_ad_analytics_configs = self._get_custom_ad_analytics_stream_configs(stream_configs, config)

        custom_ad_analytics_streams = [
            self._constructor.create_component(
                DeclarativeStreamModel, stream_config, config, emit_connector_builder_messages=self._emit_connector_builder_messages
            )
            for stream_config in self._initialize_cache_for_parent_streams(custom_ad_analytics_configs)
        ]

        return custom_ad_analytics_streams

    @staticmethod
    def _get_custom_ad_analytics_stream_configs(stream_configs: List[dict], config: Mapping[str, Any]) -> List[dict]:
        """
        Generate custom ad analytics stream configurations.

        :param stream_configs: List of default stream configurations.
        :param config: Configuration mapping containing custom ad analytics report parameters.
        :return: List of custom ad analytics stream configurations.
        """

        custom_stream_configs = []
        for stream_config in stream_configs:
            if stream_config["name"] == "ad_campaign_analytics":
                for ad_report in config.get("ad_analytics_reports", []):
                    updated_config = deepcopy(stream_config)
                    update_specific_key(
                        updated_config, "pivot", f"(value:{ad_report.get('pivot_by')})", condition_func=lambda d: d.get("q")
                    )
                    update_specific_key(
                        updated_config, "value", f"{ad_report.get('pivot_by')}", condition_func=lambda d: d.get("path") == ["pivot"]
                    )

                    # TODO: to avoid breaking changes left as is, but need to update to more adaptive way to avoid words merging
                    update_specific_key(updated_config, "name", f"custom_{ad_report.get('name')}")
                    update_specific_key(updated_config, "timeGranularity", f"(value:{ad_report.get('time_granularity')})")

                    custom_stream_configs.append(updated_config)
        return custom_stream_configs
