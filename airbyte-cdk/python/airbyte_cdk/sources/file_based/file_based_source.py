import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Mapping, Tuple, Optional

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.file_based.discovery_concurrency_policy import (
    AbstractDiscoveryConcurrencyPolicy, DefaultDiscoveryConcurrencyPolicy,
)
from airbyte_cdk.sources.file_based.file_based_stream import FileBasedStream
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
)


@dataclass
class AbstractFileBasedSource(AbstractSource, ABC):
    """
    All file-based sources must extend this class, implementing `stream_reader()`.
    """

    @abstractmethod
    def stream_reader(self, config: Mapping[str, Any]) -> AbstractFileBasedStreamReader:
        ...

    @property
    def discovery_concurrency_policy(self) -> AbstractDiscoveryConcurrencyPolicy:
        return DefaultDiscoveryConcurrencyPolicy()

    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
        """
        Check that the source can be accessed using the user-provided configuration.

        For each stream, verify that we can list and read files.

        Returns (True, None) if the connection check is successful.

        Otherwise, the "error" object should describe what went wrong.
        """
        streams = self.streams(config)
        if len(streams) == 0:
            return False, f"No streams are available for source {self.name}"

        errors = []
        for stream in streams:
            try:
                (
                    stream_is_available,
                    reason,
                ) = stream.availability_strategy.check_availability(
                    stream, logger, self
                )
            except Exception:
                errors.append(
                    f"Unable to connect to stream {stream} - {traceback.format_exc()}"
                )
            else:
                if not stream_is_available:
                    errors.append(reason)

        return bool(errors), (errors or None)

    def streams(self, config: Mapping[str, Any]) -> List[FileBasedStream]:
        """
        Return a list of this source's streams.
        """
        stream_reader = self.stream_reader(config)
        return [
            FileBasedStream(
                raw_config=stream,
                stream_reader=stream_reader,
                discovery_concurrency_policy=self.discovery_concurrency_policy,
            )
            for stream in config["streams"]
        ]
