#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import traceback
from abc import ABC
from typing import Any, Dict, List, Mapping, Optional, Tuple, Type

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.default_file_based_availability_strategy import DefaultFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy, DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types import default_parsers
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy, DefaultSchemaValidationPolicy
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream, DefaultFileBasedStream
from airbyte_cdk.sources.file_based.stream.cursor.default_file_based_cursor import DefaultFileBasedCursor
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from pydantic.error_wrappers import ValidationError


class FileBasedSource(AbstractSource, ABC):
    """
    All file-based sources must provide a `stream_reader`.
    """

    def __init__(
        self,
        stream_reader: AbstractFileBasedStreamReader,
        availability_strategy: AvailabilityStrategy,
        discovery_policy: AbstractDiscoveryPolicy = DefaultDiscoveryPolicy(),
        parsers: Dict[str, FileTypeParser] = None,
        validation_policies: Type[AbstractSchemaValidationPolicy] = Type[DefaultSchemaValidationPolicy],
    ):
        self.stream_reader = stream_reader
        self.availability_strategy = availability_strategy or DefaultFileBasedAvailabilityStrategy(stream_reader)
        self.discovery_policy = discovery_policy
        self.parsers = parsers or default_parsers
        self.validation_policies = validation_policies

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Check that the source can be accessed using the user-provided configuration.

        For each stream, verify that we can list and read files.

        Returns (True, None) if the connection check is successful.

        Otherwise, the "error" object should describe what went wrong.
        """
        streams = self.streams(config)
        if len(streams) == 0:
            return (
                False,
                f"No streams are available for source {self.name}. This is probably an issue with the connector. Please verify that your "
                f"configuration provides permissions to list and read files from the source. Contact support if you are unable to "
                f"resolve this issue.",
            )

        errors = []
        for stream in streams:
            try:
                (
                    stream_is_available,
                    reason,
                ) = stream.availability_strategy.check_availability(stream, logger, self)
            except Exception:
                errors.append(f"Unable to connect to stream {stream} - {''.join(traceback.format_exc())}")
            else:
                if not stream_is_available:
                    errors.append(reason)

        return not bool(errors), (errors or None)

    def streams(self, config: Mapping[str, Any]) -> List[AbstractFileBasedStream]:
        """
        Return a list of this source's streams.
        """
        try:
            streams = []
            for stream in config["streams"]:
                stream_config = FileBasedStreamConfig(**stream)
                streams.append(
                    DefaultFileBasedStream(
                        config=stream_config,
                        stream_reader=self.stream_reader,
                        availability_strategy=self.availability_strategy,
                        discovery_policy=self.discovery_policy,
                        parsers=self.parsers,
                        cursor=DefaultFileBasedCursor(stream_config.max_history_size, stream_config.days_to_sync_if_history_is_full),
                        validation_policies=self.validation_policies,
                    )
                )
            return streams

        except ValidationError as exc:
            raise ConfigValidationError(FileBasedSourceError.CONFIG_VALIDATION_ERROR) from exc
