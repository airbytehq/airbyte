#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from datetime import timedelta
from logging import Logger
from typing import Any, Mapping, Optional, Tuple

from pydantic import ValidationError
from requests.exceptions import InvalidURL

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.sources.declarative.exceptions import ReadException
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .utils import read_full_refresh


class SourceJira(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger: Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            streams = self.streams(config)
            stream_name_to_stream = {s.name: s for s in streams}

            # check projects
            if config.get("projects"):
                projects_stream = stream_name_to_stream["projects"]
                actual_projects = {project["key"] for project in read_full_refresh(projects_stream)}
                unknown_projects = set(config["projects"]) - actual_projects
                if unknown_projects:
                    return False, "unknown project(s): " + ", ".join(unknown_projects)

            # Get streams to check access to any of them
            for stream_name in self._source_config["check"]["stream_names"]:
                try:
                    next(read_full_refresh(stream_name_to_stream[stream_name]), None)
                except:
                    logger.warning(f"No access to stream: {stream_name}")
                else:
                    logger.info(f"API Token have access to stream: {stream_name}, so check is successful.")
                    return True, None
            return False, "This API Token does not have permission to read any of the resources."
        except ValidationError as e:
            return False, e
        except (AirbyteTracedException, ReadException, InvalidURL) as e:
            if isinstance(e, InvalidURL) or "404" in str(e) or (isinstance(e, AirbyteTracedException) and "Not found" in e.message):
                raise AirbyteTracedException(
                    message="Config validation error: please check that your domain is valid and does not include protocol (e.g: https://).",
                    internal_message=str(e),
                    failure_type=FailureType.config_error,
                ) from None
            raise e

    def _validate_and_transform_config(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")
        if start_date:
            config["start_date"] = ab_datetime_parse(start_date).to_datetime()
        config["lookback_window_minutes"] = timedelta(minutes=config.get("lookback_window_minutes", 0))
        config["projects"] = config.get("projects", [])
        return config

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        return BasicHttpAuthenticator(config.get("email"), config["api_token"])
