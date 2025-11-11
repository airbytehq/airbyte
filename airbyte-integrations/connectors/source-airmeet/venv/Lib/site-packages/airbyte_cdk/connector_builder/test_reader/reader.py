#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from math import log
from typing import Any, ClassVar, Dict, Iterator, List, Mapping, Optional, Union

from airbyte_cdk.connector_builder.models import (
    AuxiliaryRequest,
    LogMessage,
    StreamRead,
    StreamReadSlices,
)
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import (
    AirbyteControlMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    TraceType,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
)
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_format_inferrer import DatetimeFormatInferrer
from airbyte_cdk.utils.schema_inferrer import (
    SchemaInferrer,
    SchemaValidationException,
)

from .helpers import clean_config
from .message_grouper import get_message_groups
from .types import GROUPED_MESSAGES, INFERRED_SCHEMA_OUTPUT_TYPE, MESSAGE_GROUPS


class TestReader:
    """
    A utility class for performing test reads from a declarative data source, primarily used to validate
    connector configurations by performing partial stream reads.

    Initialization:

        TestReader(max_pages_per_slice: int, max_slices: int, max_record_limit: int = 1000)
            Initializes a new instance of the TestReader class with limits on pages per slice, slices, and records
            per read operation.

    Public Methods:
        run_test_read(source, config, configured_catalog, state, record_limit=None) -> StreamRead:

            Executes a test read operation from the given declarative source. It configures and infers the schema,
            processes the read messages (including logging and error handling), and returns a StreamRead object
            that contains slices of data, log messages, auxiliary requests, and any inferred schema or datetime formats.

            Parameters:
                source (ConcurrentDeclarativeSource): The data source to read from.
                config (Mapping[str, Any]): Configuration parameters for the source.
                configured_catalog (ConfiguredAirbyteCatalog): Catalog containing stream configuration.
                state (List[AirbyteStateMessage]): Current state information for the read.
                record_limit (Optional[int]): Optional override for the maximum number of records to read.

            Returns:
                StreamRead: An object encapsulating logs, data slices, auxiliary requests, and inferred metadata,
                along with indicators if any configured limit was reached.

    """

    __test__: ClassVar[bool] = False  # Tell Pytest this is not a Pytest class, despite its name

    logger = logging.getLogger("airbyte.connector-builder")

    def __init__(
        self,
        max_pages_per_slice: int,
        max_slices: int,
        max_record_limit: int = 1000,
    ) -> None:
        self._max_pages_per_slice = max_pages_per_slice
        self._max_slices = max_slices
        self._max_record_limit = max_record_limit

    def run_test_read(
        self,
        source: ConcurrentDeclarativeSource,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        stream_name: str,
        state: List[AirbyteStateMessage],
        record_limit: Optional[int] = None,
    ) -> StreamRead:
        """
        Run a test read for the connector by reading from a single stream and inferring schema and datetime formats.

        Parameters:
            source (ConcurrentDeclarativeSource): The source instance providing the streams.
            config (Mapping[str, Any]): The configuration settings to use for reading.
            configured_catalog (ConfiguredAirbyteCatalog): The catalog specifying the stream configuration.
            state (List[AirbyteStateMessage]): A list of state messages to resume the read.
            record_limit (Optional[int], optional): Maximum number of records to read. Defaults to None.

        Returns:
            StreamRead: An object containing the following attributes:
                - logs (List[str]): Log messages generated during the process.
                - slices (List[Any]): The data slices read from the stream.
                - test_read_limit_reached (bool): Indicates whether the record limit was reached.
                - auxiliary_requests (Any): Any auxiliary requests generated during reading.
                - inferred_schema (Any): The schema inferred from the stream data.
                - latest_config_update (Any): The latest configuration update, if applicable.
                - inferred_datetime_formats (Dict[str, str]): Mapping of fields to their inferred datetime formats.
        """

        record_limit = self._check_record_limit(record_limit)
        # The connector builder currently only supports reading from a single stream at a time
        streams = source.streams(config)
        stream = next((stream for stream in streams if stream.name == stream_name), None)

        # get any deprecation warnings during the component creation
        deprecation_warnings: List[LogMessage] = source.deprecation_warnings()

        schema_inferrer = SchemaInferrer(
            self._pk_to_nested_and_composite_field(
                stream.primary_key if hasattr(stream, "primary_key") else stream._primary_key  # type: ignore  # We are accessing the private property here as the primary key is not exposed. We should either expose it or use `as_airbyte_stream` to retrieve it as this is the "official" way where it is exposed in the Airbyte protocol
            )
            if stream
            else None,
            self._cursor_field_to_nested_and_composite_field(stream.cursor_field)
            if stream and stream.cursor_field
            else None,
        )
        datetime_format_inferrer = DatetimeFormatInferrer()

        message_group = get_message_groups(
            self._read_stream(source, config, configured_catalog, state),
            schema_inferrer,
            datetime_format_inferrer,
            record_limit,
            stream_name,
        )

        slices, log_messages, auxiliary_requests, latest_config_update = self._categorise_groups(
            message_group
        )

        # extend log messages with deprecation warnings
        log_messages.extend(deprecation_warnings)

        schema, log_messages = self._get_infered_schema(
            configured_catalog, schema_inferrer, log_messages
        )

        return StreamRead(
            logs=log_messages,
            slices=slices,
            test_read_limit_reached=self._has_reached_limit(slices),
            auxiliary_requests=auxiliary_requests,
            inferred_schema=schema,
            latest_config_update=self._get_latest_config_update(latest_config_update),
            inferred_datetime_formats=datetime_format_inferrer.get_inferred_datetime_formats(),
        )

    def _pk_to_nested_and_composite_field(
        self, field: Optional[Union[str, List[str], List[List[str]]]]
    ) -> List[List[str]]:
        """
        Converts a primary key definition into a nested list representation.

        The function accepts a primary key that can be a single string, a list of strings, or a list of lists of strings.
        It ensures that the return value is always a list of lists of strings.

        Parameters:
            field (Optional[Union[str, List[str], List[List[str]]]]):
                The primary key definition. This can be:
                  - None or an empty value: returns a list containing an empty list.
                  - A single string: returns a list containing one list with the string.
                  - A list of strings (composite key): returns a list where each key is encapsulated in its own list.
                  - A list of lists of strings (nested field structure): returns as is.

        Returns:
            List[List[str]]:
                A nested list representation of the primary key.
        """
        if not field:
            return [[]]

        if isinstance(field, str):
            return [[field]]

        is_composite_key = isinstance(field[0], str)
        if is_composite_key:
            return [[i] for i in field]  # type: ignore  # the type of field is expected to be List[str] here

        return field  # type: ignore  # the type of field is expected to be List[List[str]] here

    def _cursor_field_to_nested_and_composite_field(
        self, field: Union[str, List[str]]
    ) -> List[List[str]]:
        """
        Transforms the cursor field input into a nested list format suitable for further processing.

        This function accepts a cursor field specification, which can be either:
            - A falsy value (e.g., None or an empty string), in which case it returns a list containing an empty list.
            - A string representing a simple cursor field. The string is wrapped in a nested list.
            - A list of strings representing a composite or nested cursor field. The list is returned wrapped in an outer list.

        Parameters:
            field (Union[str, List[str]]): The cursor field specification. It can be:
                - An empty or falsy value: returns [[]].
                - A string: returns [[field]].
                - A list of strings: returns [field] if the first element is a string.

        Returns:
            List[List[str]]: A nested list representation of the cursor field.

        Raises:
            ValueError: If the input is a list but its first element is not a string,
                        indicating an unsupported type for a cursor field.
        """
        if not field:
            return [[]]

        if isinstance(field, str):
            return [[field]]

        is_nested_key = isinstance(field[0], str)
        if is_nested_key:
            return [field]

        raise ValueError(f"Unknown type for cursor field `{field}")

    def _check_record_limit(self, record_limit: Optional[int] = None) -> int:
        """
        Checks and adjusts the provided record limit to ensure it falls within the valid range.

        If record_limit is provided, it must be between 1 and self._max_record_limit inclusive.
        If record_limit is None, it defaults to self._max_record_limit.

        Args:
            record_limit (Optional[int]): The requested record limit to validate.

        Returns:
            int: The validated record limit. If record_limit exceeds self._max_record_limit, the maximum allowed value is used.

        Raises:
            ValueError: If record_limit is provided and is not between 1 and self._max_record_limit.
        """
        if record_limit is not None and not (1 <= record_limit <= self._max_record_limit):
            raise ValueError(
                f"Record limit must be between 1 and {self._max_record_limit}. Got {record_limit}"
            )

        if record_limit is None:
            record_limit = self._max_record_limit
        else:
            record_limit = min(record_limit, self._max_record_limit)

        return record_limit

    def _categorise_groups(self, message_groups: MESSAGE_GROUPS) -> GROUPED_MESSAGES:
        """
        Categorizes a sequence of message groups into slices, log messages, auxiliary requests, and the latest configuration update.

        This function iterates over each message group in the provided collection and processes it based on its type:
            - AirbyteLogMessage: Converts the log message into a LogMessage object and appends it to the log_messages list.
            - AirbyteTraceMessage with type ERROR: Extracts error details, creates a LogMessage at the "ERROR" level, and appends it.
            - AirbyteControlMessage: Updates the latest_config_update if the current message is more recent.
            - AuxiliaryRequest: Appends the message to the auxiliary_requests list.
            - StreamReadSlices: Appends the message to the slices list.
            - Any other type: Raises a ValueError indicating an unknown message group type.

        Parameters:
            message_groups (MESSAGE_GROUPS): A collection of message groups to be processed.

        Returns:
            GROUPED_MESSAGES: A tuple containing four elements:
                - slices: A list of StreamReadSlices objects.
                - log_messages: A list of LogMessage objects.
                - auxiliary_requests: A list of AuxiliaryRequest objects.
                - latest_config_update: The most recent AirbyteControlMessage, or None if none was processed.

        Raises:
            ValueError: If a message group of an unknown type is encountered.
        """

        slices = []
        log_messages = []
        auxiliary_requests = []
        latest_config_update: Optional[AirbyteControlMessage] = None

        # process the message groups first
        for message_group in message_groups:
            match message_group:
                case AirbyteLogMessage():
                    log_messages.append(
                        LogMessage(message=message_group.message, level=message_group.level.value)
                    )
                case AirbyteTraceMessage():
                    if message_group.type == TraceType.ERROR:
                        log_messages.append(
                            LogMessage(
                                message=message_group.error.message,  # type: ignore
                                level="ERROR",
                                internal_message=message_group.error.internal_message,  # type: ignore
                                stacktrace=message_group.error.stack_trace,  # type: ignore
                            )
                        )
                case AirbyteControlMessage():
                    if (
                        not latest_config_update
                        or latest_config_update.emitted_at <= message_group.emitted_at
                    ):
                        latest_config_update = message_group
                case AuxiliaryRequest():
                    auxiliary_requests.append(message_group)
                case StreamReadSlices():
                    slices.append(message_group)
                case _:
                    raise ValueError(f"Unknown message group type: {type(message_group)}")

        return slices, log_messages, auxiliary_requests, latest_config_update

    def _get_infered_schema(
        self,
        configured_catalog: ConfiguredAirbyteCatalog,
        schema_inferrer: SchemaInferrer,
        log_messages: List[LogMessage],
    ) -> INFERRED_SCHEMA_OUTPUT_TYPE:
        """
        Retrieves the inferred schema from the given configured catalog using the provided schema inferrer.

        This function processes a single stream from the configured catalog. It attempts to obtain the stream's
        schema via the schema inferrer. If a SchemaValidationException occurs, each validation error is logged in the
        provided log_messages list and the partially inferred schema (from the exception) is returned.

        Parameters:
            configured_catalog (ConfiguredAirbyteCatalog): The configured catalog that contains the stream metadata.
                It is assumed that only one stream is defined.
            schema_inferrer (SchemaInferrer): An instance responsible for inferring the schema for a given stream.
            log_messages (List[LogMessage]): A list that will be appended with log messages, especially error messages
                if schema validation issues arise.

        Returns:
            INFERRED_SCHEMA_OUTPUT_TYPE: A tuple consisting of the inferred schema and the updated list of log messages.
        """

        try:
            # The connector builder currently only supports reading from a single stream at a time
            configured_stream = configured_catalog.streams[0]
            schema = schema_inferrer.get_stream_schema(configured_stream.stream.name)
        except SchemaValidationException as exception:
            # we update the log_messages with possible errors
            for validation_error in exception.validation_errors:
                log_messages.append(LogMessage(validation_error, "ERROR"))
            schema = exception.schema

        return schema, log_messages

    def _get_latest_config_update(
        self,
        latest_config_update: AirbyteControlMessage | None,
    ) -> Dict[str, Any] | None:
        """
        Retrieves a cleaned configuration from the latest Airbyte control message.

        This helper function extracts the configuration from the given Airbyte control message, cleans it using the internal `Parsers.clean_config` function,
        and returns the resulting dictionary. If no control message is provided (i.e., latest_config_update is None), the function returns None.

        Parameters:
            latest_config_update (AirbyteControlMessage | None): The control message containing the connector configuration. May be None.

        Returns:
            Dict[str, Any] | None: The cleaned configuration dictionary if available; otherwise, None.
        """

        return (
            clean_config(latest_config_update.connectorConfig.config)  # type: ignore
            if latest_config_update
            else None
        )

    def _read_stream(
        self,
        source: ConcurrentDeclarativeSource,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        state: List[AirbyteStateMessage],
    ) -> Iterator[AirbyteMessage]:
        """
        Reads messages from the given ConcurrentDeclarativeSource using an AirbyteEntrypoint.

        This method attempts to yield messages from the source's read generator. If the generator
        raises an AirbyteTracedException, it checks whether the exception message indicates a non-actionable
        error (e.g., a final exception from AbstractSource that should not be logged). In that case, it stops
        processing without yielding the exception as a message. For other exceptions, the exception is caught,
        wrapped into an AirbyteTracedException, and yielded as an AirbyteMessage.

        Parameters:
            source (ConcurrentDeclarativeSource): The source object that provides data reading logic.
            config (Mapping[str, Any]): The configuration dictionary for the source.
            configured_catalog (ConfiguredAirbyteCatalog): The catalog defining the streams and their configurations.
            state (List[AirbyteStateMessage]): A list representing the current state for incremental sync.

        Yields:
            AirbyteMessage: Messages yielded from the source's generator. In case of exceptions,
            an AirbyteMessage encapsulating the error is yielded instead.
        """
        # the generator can raise an exception
        # iterate over the generated messages. if next raise an exception, catch it and yield it as an AirbyteLogMessage
        try:
            yield from AirbyteEntrypoint(source).read(
                source.spec(self.logger), config, configured_catalog, state
            )
        except AirbyteTracedException as traced_exception:
            # Look for this message which indicates that it is the "final exception" raised by AbstractSource.
            # If it matches, don't yield this as we don't need to show this in the Builder.
            # This is somewhat brittle as it relies on the message string, but if they drift then the worst case
            # is that this message will be shown in the Builder.
            if (
                traced_exception.message is not None
                and "During the sync, the following streams did not sync successfully"
                in traced_exception.message
            ):
                return
            yield traced_exception.as_airbyte_message()
        except Exception as e:
            error_message = f"{e.args[0] if len(e.args) > 0 else str(e)}"
            yield AirbyteTracedException.from_exception(
                e, message=error_message
            ).as_airbyte_message()

    def _has_reached_limit(self, slices: List[StreamReadSlices]) -> bool:
        """
        Determines whether the provided collection of slices has reached any defined limits.

        This function checks for three types of limits:
        1. If the number of slices is greater than or equal to a maximum slice limit.
        2. If any individual slice has a number of pages that meets or exceeds a maximum number of pages per slice.
        3. If the cumulative number of records across all pages in all slices reaches or exceeds a maximum record limit.

        Parameters:
            slices (List[StreamReadSlices]): A list where each element represents a slice containing one or more pages, and each page has a collection of records.

        Returns:
            bool: True if any of the following conditions is met:
                - The number of slices is at or above the maximum allowed slices.
                - Any slice contains pages at or above the maximum allowed per slice.
                - The total count of records reaches or exceeds the maximum record limit.
            False otherwise.
        """
        if len(slices) >= self._max_slices:
            return True

        record_count = 0

        for _slice in slices:
            if len(_slice.pages) >= self._max_pages_per_slice:
                return True
            for page in _slice.pages:
                record_count += len(page.records)
                if record_count >= self._max_record_limit:
                    return True
        return False
