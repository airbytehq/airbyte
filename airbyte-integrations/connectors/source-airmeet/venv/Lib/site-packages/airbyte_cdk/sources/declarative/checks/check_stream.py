#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import traceback
from dataclasses import InitVar, dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy


def evaluate_availability(
    stream: Union[Stream, AbstractStream], logger: logging.Logger
) -> Tuple[bool, Optional[str]]:
    """
    As a transition period, we want to support both Stream and AbstractStream until we migrate everything to AbstractStream.
    """
    if isinstance(stream, Stream):
        return HttpAvailabilityStrategy().check_availability(stream, logger)
    elif isinstance(stream, AbstractStream):
        availability = stream.check_availability()
        return availability.is_available, availability.reason
    else:
        raise ValueError(f"Unsupported stream type {type(stream)}")


@dataclass(frozen=True)
class DynamicStreamCheckConfig:
    """Defines the configuration for dynamic stream during connection checking. This class specifies
    what dynamic streams  in the stream template should be updated with value, supporting dynamic interpolation
    and type enforcement."""

    dynamic_stream_name: str
    stream_count: int = 0


@dataclass
class CheckStream(ConnectionChecker):
    """
    Checks the connections by checking availability of one or many streams selected by the developer

    Attributes:
        stream_name (List[str]): names of streams to check
    """

    stream_names: List[str]
    parameters: InitVar[Mapping[str, Any]]
    dynamic_streams_check_configs: Optional[List[DynamicStreamCheckConfig]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        if self.dynamic_streams_check_configs is None:
            self.dynamic_streams_check_configs = []

    def _log_error(self, logger: logging.Logger, action: str, error: Exception) -> Tuple[bool, str]:
        """Logs an error and returns a formatted error message."""
        error_message = f"Encountered an error while {action}. Error: {error}"
        logger.error(error_message + f"Error traceback: \n {traceback.format_exc()}", exc_info=True)
        return False, error_message

    def check_connection(
        self,
        source: Source,
        logger: logging.Logger,
        config: Mapping[str, Any],
    ) -> Tuple[bool, Any]:
        """Checks the connection to the source and its streams."""
        try:
            streams: List[Union[Stream, AbstractStream]] = source.streams(config=config)  # type: ignore  # this is a migration step and we expect the declarative CDK to migrate off of ConnectionChecker
            if not streams:
                return False, f"No streams to connect to from source {source}"
        except Exception as error:
            return self._log_error(logger, "discovering streams", error)

        stream_name_to_stream = {s.name: s for s in streams}
        for stream_name in self.stream_names:
            if stream_name not in stream_name_to_stream:
                raise ValueError(
                    f"{stream_name} is not part of the catalog. Expected one of {list(stream_name_to_stream.keys())}."
                )

            stream_availability, message = self._check_stream_availability(
                stream_name_to_stream, stream_name, logger
            )
            if not stream_availability:
                return stream_availability, message

        should_check_dynamic_streams = (
            hasattr(source, "resolved_manifest")
            and hasattr(source, "dynamic_streams")
            and self.dynamic_streams_check_configs
        )

        if should_check_dynamic_streams:
            return self._check_dynamic_streams_availability(source, stream_name_to_stream, logger)

        return True, None

    def _check_stream_availability(
        self,
        stream_name_to_stream: Dict[str, Union[Stream, AbstractStream]],
        stream_name: str,
        logger: logging.Logger,
    ) -> Tuple[bool, Any]:
        """Checks if streams are available."""
        try:
            stream = stream_name_to_stream[stream_name]
            stream_is_available, reason = evaluate_availability(stream, logger)
            if not stream_is_available:
                message = f"Stream {stream_name} is not available: {reason}"
                logger.warning(message)
                return stream_is_available, message
        except Exception as error:
            return self._log_error(logger, f"checking availability of stream {stream_name}", error)
        return True, None

    def _check_dynamic_streams_availability(
        self,
        source: Source,
        stream_name_to_stream: Dict[str, Union[Stream, AbstractStream]],
        logger: logging.Logger,
    ) -> Tuple[bool, Any]:
        """Checks the availability of dynamic streams."""
        dynamic_streams = source.resolved_manifest.get("dynamic_streams", [])  # type: ignore[attr-defined] # The source's resolved_manifest manifest is checked before calling this method
        dynamic_stream_name_to_dynamic_stream = {
            ds.get("name", f"dynamic_stream_{i}"): ds for i, ds in enumerate(dynamic_streams)
        }
        generated_streams = self._map_generated_streams(source.dynamic_streams)  # type: ignore[attr-defined] # The source's dynamic_streams manifest is checked before calling this method

        for check_config in self.dynamic_streams_check_configs:  # type: ignore[union-attr] # None value for self.dynamic_streams_check_configs handled in __post_init__
            if check_config.dynamic_stream_name not in dynamic_stream_name_to_dynamic_stream:
                return (
                    False,
                    f"Dynamic stream {check_config.dynamic_stream_name} is not found in manifest.",
                )

            generated = generated_streams.get(check_config.dynamic_stream_name, [])
            stream_availability, message = self._check_generated_streams_availability(
                generated, stream_name_to_stream, logger, check_config.stream_count
            )
            if not stream_availability:
                return stream_availability, message

        return True, None

    def _map_generated_streams(
        self, dynamic_streams: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Maps dynamic stream names to their corresponding generated streams."""
        mapped_streams: Dict[str, List[Dict[str, Any]]] = {}
        for stream in dynamic_streams:
            mapped_streams.setdefault(stream["dynamic_stream_name"], []).append(stream)
        return mapped_streams

    def _check_generated_streams_availability(
        self,
        generated_streams: List[Dict[str, Any]],
        stream_name_to_stream: Dict[str, Union[Stream, AbstractStream]],
        logger: logging.Logger,
        max_count: int,
    ) -> Tuple[bool, Any]:
        """Checks availability of generated dynamic streams."""
        for declarative_stream in generated_streams[: min(max_count, len(generated_streams))]:
            stream = stream_name_to_stream[declarative_stream["name"]]
            try:
                stream_is_available, reason = evaluate_availability(stream, logger)
                if not stream_is_available:
                    message = f"Dynamic Stream {stream.name} is not available: {reason}"
                    logger.warning(message)
                    return False, message
            except Exception as error:
                return self._log_error(
                    logger, f"checking availability of dynamic stream {stream.name}", error
                )
        return True, None
