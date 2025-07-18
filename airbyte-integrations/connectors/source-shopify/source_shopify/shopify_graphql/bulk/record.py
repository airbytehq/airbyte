#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass, field
from functools import cached_property
from io import TextIOWrapper
from json import loads
from os import remove
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Union

from source_shopify.utils import LOGGER

from .exceptions import ShopifyBulkExceptions
from .query import ShopifyBulkQuery
from .tools import END_OF_FILE, BulkTools


@dataclass
class ShopifyBulkRecord:
    """
    ShopifyBulkRecord is a class designed to handle the processing of bulk records from Shopify's GraphQL API.

    Attributes:
        query (ShopifyBulkQuery): The query object associated with the bulk record.
        parent_stream_name (Optional[str]): The name of the parent stream, if any.
        parent_stream_cursor (Optional[str]): The cursor of the parent stream, if any.
        buffer (List[MutableMapping[str, Any]]): A buffer to store records before processing.
        composition (Optional[Mapping[str, Any]]): The composition of the record, derived from the query.
        record_process_components (Optional[Callable[[MutableMapping], MutableMapping]]): A callable to process record components.
        components (List[str]): A list of components derived from the record composition.
        _parent_stream_cursor_value (Optional[str | int]): The current value of the parent stream cursor.
        record_composed (int): The count of records composed.

    Methods:
        __post_init__(): Initializes additional attributes after the object is created.
        tools(): Returns an instance of BulkTools.
        has_parent_stream(): Checks if the record has a parent stream.
        parent_cursor_key(): Returns the key for the parent cursor if a parent stream exists.
        check_type(record, types): Checks if the record's type matches the given type(s).
        _parse_parent_state_value(value): Parses the parent state value and converts it to the appropriate format.
        _set_parent_state_value(value): Sets the parent state value by parsing the provided value and updating the parent stream cursor value.
        _track_parent_cursor(record): Tracks the cursor value from the parent stream if it exists and updates the parent state.
        get_parent_stream_state(): Retrieves the state of the parent stream if it exists.
        record_new(record): Processes a new record by preparing it, removing the "__typename" key, and appending it to the buffer.
        record_new_component(record): Processes a new record by extracting its component type and adding it to the appropriate placeholder in the components list.
        component_prepare(record): Prepares the given record by initializing a "record_components" dictionary.
        buffer_flush(): Flushes the buffer by processing each record in the buffer.
        record_compose(record): Processes a given record and yields buffered records if certain conditions are met.
        process_line(jsonl_file): Processes a JSON Lines (jsonl) file and yields records.
        record_resolve_id(record): Resolves and updates the 'id' field in the given record.
        produce_records(filename): Reads the JSONL content saved from `job.job_retrieve_result()` line-by-line to avoid OOM.
        read_file(filename, remove_file): Reads a file and produces records from it.
    """

    query: ShopifyBulkQuery
    parent_stream_name: Optional[str] = None
    parent_stream_cursor: Optional[str] = None

    # default buffer
    buffer: List[MutableMapping[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.composition: Optional[Mapping[str, Any]] = self.query.record_composition
        self.record_process_components: Optional[Callable[[MutableMapping], MutableMapping]] = self.query.record_process_components
        self.components: List[str] = self.composition.get("record_components", []) if self.composition else []
        # We track the parent state for BULK substreams outside of the main CDK methods,
        # to be able to update the moving parent state when there are no substream records to emit.
        self._parent_stream_cursor_value: Optional[str | int] = None
        # how many records composed
        self.record_composed: int = 0

    @cached_property
    def tools(self) -> BulkTools:
        return BulkTools()

    @cached_property
    def has_parent_stream(self) -> bool:
        return True if self.parent_stream_name and self.parent_stream_cursor else False

    @cached_property
    def parent_cursor_key(self) -> Optional[str]:
        if self.has_parent_stream:
            return f"{self.parent_stream_name}_{self.parent_stream_cursor}"

    @staticmethod
    def check_type(record: Mapping[str, Any], types: Union[List[str], str]) -> bool:
        """
        Check if the record's type matches the given type(s).

        Args:
            record (Mapping[str, Any]): The record to check, expected to have a "__typename" key.
            types (Union[List[str], str]): The type(s) to check against. Can be a single type (str) or a list of types (List[str]).

        Returns:
            bool: True if the record's type matches one of the given types, False otherwise.
        """

        record_type = record.get("__typename")
        if isinstance(types, list):
            return any(record_type == t for t in types)
        else:
            return record_type == types

    def _parse_parent_state_value(self, value: str | int) -> str | int:
        """
        Parses the parent state value and converts it to the appropriate format.

        If the value is a string, it converts it to RFC 3339 datetime format using the `_datetime_str_to_rfc3339` method.
        If the value is an integer, it returns the value as is.

        Args:
            value (str | int): The parent state value to be parsed.

        Returns:
            str | int: The parsed parent state value in the appropriate format.
        """

        if isinstance(value, str):
            return self.tools._datetime_str_to_rfc3339(value)
        elif isinstance(value, int):
            return value

    def _set_parent_state_value(self, value: str | int) -> None:
        """
        Sets the parent state value by parsing the provided value and updating the
        parent stream cursor value. If the parent stream cursor value is already set,
        it updates it to the maximum of the current and parsed values.

        Args:
            value (str | int): The value to be parsed and set as the parent state value.
        """

        parsed_value = self._parse_parent_state_value(value)
        if not self._parent_stream_cursor_value:
            self._parent_stream_cursor_value = parsed_value
        else:
            self._parent_stream_cursor_value = max(self._parent_stream_cursor_value, parsed_value)

    def _track_parent_cursor(self, record: MutableMapping[str, Any]) -> None:
        """
        Tracks the cursor value from the parent stream if it exists and updates the parent state.

        Args:
            record (MutableMapping[str, Any]): The record from which to extract the parent cursor value.

        Returns:
            None
        """

        if self.has_parent_stream:
            cursor_value: Optional[str | int] = record.get(self.parent_cursor_key, None)
            if cursor_value:
                self._set_parent_state_value(cursor_value)

    def get_parent_stream_state(self) -> Optional[Union[str, Mapping[str, Any]]]:
        """
        Retrieve the state of the parent stream if it exists.

        Returns:
            Optional[Union[str, Mapping[str, Any]]]: A dictionary containing the parent stream cursor and its value
            if the parent stream exists and has a cursor value, otherwise None.
        """

        if self.has_parent_stream and self._parent_stream_cursor_value:
            return {self.parent_stream_cursor: self._parent_stream_cursor_value}

    def record_new(self, record: MutableMapping[str, Any]) -> None:
        """
        Processes a new record by preparing it, removing the "__typename" key, and appending it to the buffer.

        Args:
            record (MutableMapping[str, Any]): The record to be processed.
        """

        record = self.component_prepare(record)
        record.pop("__typename")
        self.buffer.append(record)

    def record_new_component(self, record: MutableMapping[str, Any]) -> None:
        """
        Processes a new record by extracting its component type and adding it to the appropriate
        placeholder in the components list.

        Args:
            record (MutableMapping[str, Any]): The record to be processed.
            It is expected to contain a "__typename" key which indicates the component type.
        """

        component = record.get("__typename")
        record.pop("__typename")
        # add component to its placeholder in the components list
        self.buffer[-1]["record_components"][component].append(record)

    def component_prepare(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Prepares the given record by initializing a "record_components" dictionary.

        If the instance has components, this method will add a "record_components" key to the record,
        with each component as a key and an empty list as its value.

        Args:
            record (MutableMapping[str, Any]): The record to be prepared.

        Returns:
            MutableMapping[str, Any]: The updated record with initialized "record_components".
        """

        if self.components:
            record["record_components"] = {}
            for component in self.components:
                record["record_components"][component] = []
        return record

    def buffer_flush(self) -> Iterable[Mapping[str, Any]]:
        """
        Flushes the buffer by processing each record in the buffer.

        For each record in the buffer:
        - Tracks the parent state using `_track_parent_cursor`.
        - Resolves the record ID from `str` to `int` using `record_resolve_id`.
        - Processes record components using `record_process_components`.

        Yields:
            Iterable[Mapping[str, Any]]: Processed records from the buffer.

        After processing, the buffer is cleared.
        """

        if len(self.buffer) > 0:
            for record in self.buffer:
                # track the parent state
                self._track_parent_cursor(record)
                # resolve id from `str` to `int`
                record = self.record_resolve_id(record)
                # process record components
                yield from self.record_process_components(record)
            # clean the buffer
            self.buffer.clear()

    def record_compose(self, record: Mapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Processes a given record and yields buffered records if certain conditions are met.

        Args:
            record (Mapping[str, Any]): The record to be processed.

        Returns:
            Optional[Iterable[MutableMapping[str, Any]]]: An iterable of buffered records if conditions are met, otherwise None.

        The method performs the following steps:
        1. Checks if the record matches the type specified in the "new_record" composition.
           - If it matches, it yields any buffered records from previous iterations and registers the new record.
        2. Checks if the record matches any of the specified components.
           - If it matches, it registers the new component record.

        Step 1: register the new record by it's `__typename`
        Step 2: check for `components` by their `__typename` and add to the placeholder
        Step 3: repeat until the `<END_OF_FILE>`.
        """

        if self.check_type(record, self.composition.get("new_record")):
            # emit from previous iteration, if present
            yield from self.buffer_flush()
            # register the record
            self.record_new(record)
        # components check
        elif self.check_type(record, self.components):
            self.record_new_component(record)

    def process_line(self, jsonl_file: TextIOWrapper) -> Iterable[MutableMapping[str, Any]]:
        """
        Processes a JSON Lines (jsonl) file and yields records.

        Args:
            jsonl_file (TextIOWrapper): A file-like object containing JSON Lines data.

        Yields:
            Iterable[MutableMapping[str, Any]]: An iterable of dictionaries representing the processed records.

        The method reads each line from the provided jsonl_file. It exits the loop when it encounters the <end_of_file> marker.
        For non-empty lines, it parses the JSON content and yields the resulting records. Finally, it emits any remaining
        records in the buffer.
        """

        for line in jsonl_file:
            if line == END_OF_FILE:
                break
            elif line != "":
                yield from self.record_compose(loads(line))

        # emit what's left in the buffer, typically last record
        yield from self.buffer_flush()

    def record_resolve_id(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Resolves and updates the 'id' field in the given record.

        This method extracts the 'id' from the record, checks if it is a string,
        and if so, assigns it to 'admin_graphql_api_id' in the record. It then
        resolves the string 'id' to an integer using the 'resolve_str_id' method
        from the 'tools' attribute and updates the 'id' field in the record.

        Args:
            record (MutableMapping[str, Any]): The record containing the 'id' field to be resolved.
            Example:
                { "Id": "gid://shopify/Order/19435458986123"}

        Returns:
            MutableMapping[str, Any]: The updated record with the resolved 'id' field.
            Example:
                { "id": 19435458986123, "admin_graphql_api_id": "gid://shopify/Order/19435458986123"}
        """

        id = record.get("id")
        if id and isinstance(id, str):
            record["admin_graphql_api_id"] = id
            record["id"] = self.tools.resolve_str_id(id)
        return record

    def produce_records(self, filename: str) -> Iterable[MutableMapping[str, Any]]:
        """
        Produce records from a JSON Lines (jsonl) file.

        This method reads a JSON Lines file, processes each line, converts the field names to snake_case,
        and yields each processed record. It also keeps track of the number of records processed.

        Args:
            filename (str): The path to the JSON Lines file.

        Yields:
            MutableMapping[str, Any]: A dictionary representing a processed record with field names in snake_case.
        """

        with open(filename, "r") as jsonl_file:
            # reset the counter
            self.record_composed = 0

            for record in self.process_line(jsonl_file):
                yield self.tools.fields_names_to_snake_case(record)
                self.record_composed += 1

    def read_file(self, filename: str, remove_file: Optional[bool] = True) -> Iterable[Mapping[str, Any]]:
        """
        Read the JSONL content saved from `job.job_retrieve_result()` line-by-line to avoid OOM.

        Args:
            filename (str): The name of the file to read.
            remove_file (Optional[bool]): Flag indicating whether to remove the file after reading. Defaults to True.

            Example:
                Note: typically the `filename` is taken from the `result_url` string provided in the response.

                `bulk-4039263649981.jsonl` :
                    - the `4039263649981` is the `id` of the COMPLETED BULK Jobw with `result_url`

        Yields:
            Iterable[Mapping[str, Any]]: An iterable of records produced from the file.

        Raises:
            ShopifyBulkExceptions.BulkRecordProduceError: If an error occurs while producing records from the file.

        Logs:
            Logs an info message if the file removal fails.
        """

        try:
            # produce records from saved result
            yield from self.produce_records(filename)
        except Exception as e:
            raise ShopifyBulkExceptions.BulkRecordProduceError(
                f"An error occured while producing records from BULK Job result. Trace: {repr(e)}.",
            )
        finally:
            # removing the tmp file, if requested
            if remove_file and filename:
                try:
                    remove(filename)
                except Exception as e:
                    LOGGER.info(f"Failed to remove the `tmp job result` file, the file doen't exist. Details: {repr(e)}.")
                    pass
