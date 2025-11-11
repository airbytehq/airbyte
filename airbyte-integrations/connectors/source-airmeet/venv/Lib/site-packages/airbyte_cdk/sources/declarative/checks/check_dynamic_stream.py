#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Tuple, Union

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.declarative.checks.check_stream import evaluate_availability
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream


@dataclass
class CheckDynamicStream(ConnectionChecker):
    """
    Checks the connections by checking availability of one or many dynamic streams

    Attributes:
        stream_count (int): numbers of streams to check
    """

    # TODO: Add field stream_names to check_connection for static streams
    #  https://github.com/airbytehq/airbyte-python-cdk/pull/293#discussion_r1934933483

    stream_count: int
    parameters: InitVar[Mapping[str, Any]]
    use_check_availability: bool = True

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def check_connection(
        self,
        source: Source,
        logger: logging.Logger,
        config: Mapping[str, Any],
    ) -> Tuple[bool, Any]:
        streams: List[Union[Stream, AbstractStream]] = source.streams(config=config)  # type: ignore  # this is a migration step and we expect the declarative CDK to migrate off of ConnectionChecker

        if len(streams) == 0:
            return False, f"No streams to connect to from source {source}"
        if not self.use_check_availability:
            return True, None

        try:
            for stream in streams[: min(self.stream_count, len(streams))]:
                stream_is_available, reason = evaluate_availability(stream, logger)
                if not stream_is_available:
                    message = f"Stream {stream.name} is not available: {reason}"
                    logger.warning(message)
                    return False, message
        except Exception as error:
            error_message = (
                f"Encountered an error trying to connect to stream {stream.name}. Error: {error}"
            )
            logger.error(error_message, exc_info=True)
            return False, error_message

        return True, None
