import logging
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Iterable, Optional, List, Tuple, Union, Any, Mapping

from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import Partition
from airbyte_cdk.sources.utils.transform import TypeTransformer, TransformConfig
from airbyte_cdk.sources.utils.types import StreamData
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.models import SyncMode


class AbstractStream(ABC):
    @abstractmethod
    def read(
            self, cursor_field: Optional[List[str]], logger: logging.Logger, slice_logger: SliceLogger, internal_config: InternalConfig = InternalConfig()
    ) -> Iterable[StreamData]:
        """
        Read a stream in full refresh mode
        :param stream: The stream to read data from
        :param cursor_field:
        :param logger:
        :param slice_logger:
        :param internal_config:
        :return: The stream's records
        """

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.streams.{self.name}")


    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return casing.camel_to_snake(self.__class__.__name__)

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method does not return user-friendly messages for any exception type, but it should be overriden as needed.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        return None

    @abstractmethod
    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        """
        Checks whether this stream is available.

        :param logger: source logger
        :param source: (optional) source
        :return: A tuple of (boolean, str). If boolean is true, then this stream
          is available, and no str is required. Otherwise, this stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """

    @property
    @abstractmethod
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """


    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """

    # TypeTransformer object to perform output data transformation
    transformer: TypeTransformer = TypeTransformer(TransformConfig.NoTransform)

    @lru_cache(maxsize=None)
    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """

    @property
    def supports_incremental(self) -> bool:
        """
        :return: True if this stream supports incrementally reading data
        """
        return len(self._wrapped_cursor_field()) > 0

    def _wrapped_cursor_field(self) -> List[str]:
        return [self.cursor_field] if isinstance(self.cursor_field, str) else self.cursor_field

    @abstractmethod
    def generate_partitions(self, sync_mode: SyncMode, cursor_field: Optional[List[str]]) -> Iterable[Partition]:
        pass
