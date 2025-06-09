#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Optional, Tuple

import pendulum

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams.core import Stream
from source_instagram.api import InstagramAPI
from source_instagram.streams import UserInsights


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceInstagram(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            self._validate_start_date(config)
            api = InstagramAPI(access_token=config["access_token"])
            logger.info(f"Available accounts: {api.accounts}")
        except Exception as exc:
            error_msg = repr(exc)
            return False, error_msg
        return super().check_connection(logger, config)

    def _validate_start_date(self, config):
        # If start_date is not found in config, set it to 2 years ago
        if not config.get("start_date"):
            config["start_date"] = pendulum.now().subtract(years=2).in_timezone("UTC").format("YYYY-MM-DDTHH:mm:ss.SSS[Z]")
        else:
            if pendulum.parse(config["start_date"]) > pendulum.now():
                raise ValueError("Please fix the start_date parameter in config, it cannot be in the future")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config)
        return streams + self.get_non_low_code_streams(config=config)

    def get_non_low_code_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        api = InstagramAPI(access_token=config["access_token"])
        self._validate_start_date(config)
        streams = [UserInsights(api=api, start_date=config["start_date"])]
        return streams
