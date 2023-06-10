#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import traceback
from abc import ABC
from typing import Any, Dict, List, Mapping, Optional, Tuple, Type

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy, DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types import AvroParser, CsvParser, JsonlParser, ParquetParser
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import FileType
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream, DefaultFileBasedStream

default_parsers = {
    FileType.Avro: AvroParser(),
    FileType.Csv: CsvParser(),
    FileType.Jsonl: JsonlParser(),
    FileType.Parquet: ParquetParser(),
}


class FileBasedSource(AbstractSource, ABC):
    """
    All file-based sources must provide a `stream_reader`.
    """

    def __init__(
        self,
        stream_reader: AbstractFileBasedStreamReader,
        availability_strategy: AbstractFileBasedAvailabilityStrategy,
        discovery_policy: AbstractDiscoveryPolicy = DefaultDiscoveryPolicy(),
        parsers: Dict[FileType, FileTypeParser] = None,
        stream_cls: Type[AbstractFileBasedStream] = DefaultFileBasedStream,
    ):
        self.stream_reader = stream_reader
        self.stream_cls = stream_cls
        self.availability_strategy = availability_strategy
        self.parsers = parsers or default_parsers
        self.discovery_policy = discovery_policy

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
                f"No streams are available for source {self.name}. This is probably an issue with the connector. Please contact support. ",
            )

        errors = []
        for stream in streams:
            try:
                (
                    stream_is_available,
                    reason,
                ) = stream.availability_strategy.check_availability(stream, logger, self)
            except Exception:
                errors.append(f"Unable to connect to stream {stream} - {traceback.format_exc()}")
            else:
                if not stream_is_available:
                    errors.append(reason)

        return not bool(errors), (errors or None)

    def streams(self, config: Mapping[str, Any]) -> List[AbstractFileBasedStream]:
        """
        Return a list of this source's streams.
        """
        return [
            self.stream_cls(
                raw_config=stream,
                stream_reader=self.stream_reader,
                availability_strategy=self.availability_strategy,
                discovery_policy=self.discovery_policy,
                parsers=self.parsers,
            )
            for stream in config["streams"]
        ]
