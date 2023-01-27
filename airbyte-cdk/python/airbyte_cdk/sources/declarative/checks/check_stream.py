#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import traceback
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.source import Source
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class CheckStream(ConnectionChecker, JsonSchemaMixin):
    """
    Checks the connections by checking availability of one or many streams selected by the developer

    Attributes:
        stream_name (List[str]): names of streams to check
    """

    stream_names: List[str]
    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._options = options

    def check_connection(self, source: Source, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        streams = source.streams(config)
        stream_name_to_stream = {s.name: s for s in streams}
        if len(streams) == 0:
            return False, f"No streams to connect to from source {source}"
        for stream_name in self.stream_names:
            if stream_name not in stream_name_to_stream.keys():
                raise ValueError(f"{stream_name} is not part of the catalog. Expected one of {stream_name_to_stream.keys()}.")

            stream = stream_name_to_stream[stream_name]
            availability_strategy = stream.availability_strategy or HttpAvailabilityStrategy()
            try:
                stream_is_available, reason = availability_strategy.check_availability(stream, logger, source)
                if stream_is_available:
                    return True, None
                else:
                    return False, reason
            except Exception as error:
                logger.error(f"Encountered an error trying to connect to stream {stream_name}. Error: \n {traceback.format_exc()}")
                return False, f"Unable to connect to stream {stream_name} - {error}"
