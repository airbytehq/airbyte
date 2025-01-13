#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
import traceback
from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy


class SourceAirtable(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        if len(self.streams(config)) > 0:
            stream = self.streams(config)[0]
        else:
            return (
                False,
                "Provided source configuration does not contain any streams. "
                "Please check that you have permissions to pull available tables and bases using `Metadata API` for a given authenticated user",
            )
        availability_strategy = HttpAvailabilityStrategy()
        try:
            stream_is_available, reason = availability_strategy.check_availability(stream, logger)
            if not stream_is_available:
                return False, reason
        except Exception as error:
            logger.error(f"Encountered an error trying to connect to stream {stream.name}. Error: \n {traceback.format_exc()}")
            return False, f"Unable to connect to stream {stream.name} - {error}"

        return True, None
