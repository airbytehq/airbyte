#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import pendulum

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException


def raise_config_error(message: str, original_error: Optional[Exception] = None):
    config_error = AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)
    if original_error:
        raise config_error from original_error
    raise config_error


class SourceMixpanel(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def _validate_and_transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        credentials = config.get("credentials")
        if not credentials.get("option_title"):
            if credentials.get("api_secret"):
                credentials["option_title"] = "Project Secret"
            else:
                credentials["option_title"] = "Service Account"
                if not credentials.get("project_id"):
                    raise_config_error("Required parameter 'project_id' missing or malformed. Please provide a valid project ID.")

        if config.get("project_timezone"):
            try:
                pendulum.timezone(config["project_timezone"])
            except pendulum.tz.zoneinfo.exceptions.InvalidTimezone as e:
                raise_config_error(f"Could not parse time zone: {config['project_timezone']}, please enter a valid timezone.", e)

        if not config.get("region"):
            # US is default region according to the spec
            config["region"] = "US"

        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform_config(config)

        streams = super().streams(config=config)

        return streams
