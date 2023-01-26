#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timedelta
from functools import lru_cache
from traceback import format_exc
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import FailureType
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams import Stream
from wcmatch.glob import GLOBSTAR, SPLIT, globmatch

from ..exceptions import S3Exception
from .file_info import FileInfo
from .formats.abstract_file_parser import AbstractFileParser
from .formats.avro_parser import AvroParser
from .formats.csv_parser import CsvParser
from .formats.jsonl_parser import JsonlParser
from .formats.parquet_parser import ParquetParser
from .storagefile import StorageFile

JSON_TYPES = ["string", "number", "integer", "object", "array", "boolean", "null"]

LOGGER = AirbyteLogger()


class ConfigurationError(Exception):
    """Client mis-configured"""


class FileStream(Stream, ABC):
    @property
    def fileformatparser_map(self) -> Mapping[str, type]:
        """Mapping where every key is equal  'filetype' and values are  corresponding  parser classes."""
        return {
            "csv": CsvParser,
            "parquet": ParquetParser,
            "avro": AvroParser,
            "jsonl": JsonlParser,
        }

    # TODO: make these user configurable in spec.json
    ab_additional_col = "_ab_additional_properties"
    ab_last_mod_col = "_ab_source_file_last_modified"
    ab_file_name_col = "_ab_source_file_url"
    airbyte_columns = [ab_additional_col, ab_last_mod_col, ab_file_name_col]
    datetime_format_string = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, dataset: str, provider: dict, format: dict, path_pattern: str, schema: str = None):
        """
        :param dataset: table name for this stream
        :param provider: provider specific mapping as described in spec.json
        :param format: file format specific mapping as described in spec.json
        :param path_pattern: glob-style pattern for file-matching (https://facelessuser.github.io/wcmatch/glob/)
        :param schema: JSON-syntax user provided schema, defaults to None
        """
        self.dataset = dataset
        self._path_pattern = path_pattern
        self._provider = provider
        self._format = format
        self._schema: Dict[str, Any] = {}
        if schema:
            self._schema = self._parse_user_input_schema(schema)
        self.master_schema: Dict[str, Any] = None
        LOGGER.info(f"initialised stream with format: {format}")

    @staticmethod
    def _parse_user_input_schema(schema: str) -> Dict[str, Any]:
        """
        If the user provided a schema, we run this method to convert to a python dict and verify it
        This verifies:
            - that the provided string is valid JSON
            - that it is a key:value map with no nested values (objects or arrays)
            - that all values in the map correspond to a JsonSchema datatype
        If this passes, we are confident that the user-provided schema is valid and will work as expected with the rest of the code

        :param schema: JSON-syntax user provided schema
        :raises ConfigurationError: if any of the verification steps above fail
        :return: the input schema (json string) as a python dict
        """
        try:
            py_schema: Dict[str, Any] = json.loads(schema)
        except json.decoder.JSONDecodeError as err:
            error_msg = f"Failed to parse schema {repr(err)}\n{schema}\n{format_exc()}"
            raise ConfigurationError(error_msg) from err
        # enforce all keys and values are of type string as required (i.e. no nesting)
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in py_schema.items()):
            raise ConfigurationError("Invalid schema provided, all column names and datatypes must be in string format")
        # enforce all values (datatypes) are valid JsonSchema datatypes
        if any(datatype not in JSON_TYPES for datatype in py_schema.values()):
            raise ConfigurationError(f"Invalid schema provided, datatypes must each be one of {JSON_TYPES}")

        return py_schema

    @property
    def name(self) -> str:
        return self.dataset

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    @property
    def fileformatparser_class(self) -> type:
        """
        :return: reference to the relevant fileformatparser class e.g. CsvParser
        """
        filetype = self._format.get("filetype")
        file_reader = self.fileformatparser_map.get(filetype)
        if not file_reader:
            raise RuntimeError(
                f"Detected mismatched file format '{filetype}'. Available values: '{list(self.fileformatparser_map.keys())}''."
            )
        return file_reader

    @property
    @abstractmethod
    def storagefile_class(self) -> type:
        """
        Override this to point to the relevant provider-specific StorageFile class e.g. S3File

        :return: reference to relevant class
        """

    @abstractmethod
    def filepath_iterator(self) -> Iterator[FileInfo]:
        """
        Provider-specific method to iterate through bucket/container/etc. and yield each full filepath.
        This should supply the 'FileInfo' to use in StorageFile(). This is aggrigate all file properties (last_modified, key, size).
        All this meta options are saved during loading of files' list at once.

        :yield: FileInfo object to use in StorageFile()
        """

    def pattern_matched_filepath_iterator(self, file_infos: Iterable[FileInfo]) -> Iterator[FileInfo]:
        """
        iterates through iterable file_infos and yields only those file_infos that match user-provided path patterns

        :param file_infos: filepath_iterator(), this is a param rather than method reference in order to unit test this
        :yield: FileInfo object to use in StorageFile(), if matching on user-provided path patterns
        """
        for file_info in file_infos:
            if globmatch(file_info.key, self._path_pattern, flags=GLOBSTAR | SPLIT):
                yield file_info

    @lru_cache(maxsize=None)
    def get_time_ordered_file_infos(self) -> List[FileInfo]:
        """
        Iterates through pattern_matched_filepath_iterator(), acquiring FileInfo objects
        with last_modified property of each file to return in time ascending order.
        Caches results after first run of method to avoid repeating network calls as this is used more than once

        :return: list in time-ascending order
        """
        return sorted(self.pattern_matched_filepath_iterator(self.filepath_iterator()), key=lambda file_info: file_info.last_modified)

    def _get_schema_map(self) -> Mapping[str, Any]:
        return_schema: Dict[str, Any] = None
        if self._schema != {}:
            return_schema = deepcopy(self._schema)
        else:  # we have no provided schema or schema state from a previous incremental run
            return_schema = self._get_master_schema()

        return_schema[self.ab_additional_col] = "object"
        return_schema[self.ab_last_mod_col] = "string"
        return_schema[self.ab_file_name_col] = "string"
        return return_schema

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: the JSON schema representing this stream.
        """
        # note: making every non-airbyte column nullable for compatibility
        # TODO: ensure this behaviour still makes sense as we add new file formats
        properties: Mapping[str, Any] = {
            column: {"type": ["null", typ]} if column not in self.airbyte_columns else {"type": typ}
            for column, typ in self._get_schema_map().items()
        }

        properties[self.ab_last_mod_col]["format"] = "date-time"
        return {"type": "object", "properties": properties}

    @staticmethod
    def _broadest_type(type_1: str, type_2: str) -> Optional[str]:
        non_comparable_types = ["object", "array", "null"]
        if type_1 in non_comparable_types or type_2 in non_comparable_types:
            return None
        types = {type_1, type_2}
        if types == {"boolean", "string"}:
            return "string"
        if types == {"integer", "number"}:
            return "number"
        if types == {"integer", "string"}:
            return "string"
        if types == {"number", "string"}:
            return "string"

    def _get_master_schema(self, min_datetime: datetime = None) -> Dict[str, Any]:
        """
        In order to auto-infer a schema across many files and/or allow for additional properties (columns),
            we need to determine the superset of schemas across all relevant files.
        This method iterates through get_time_ordered_file_infos() obtaining the inferred schema (process implemented per file format),
            to build up this superset schema (master_schema).
        This runs datatype checks to Warn or Error if we find incompatible schemas (e.g. same column is 'date' in one file but 'float' in another).
        This caches the master_schema after first run in order to avoid repeated compute and network calls to infer schema on all files.

        :param min_datetime: if passed, will only use files with last_modified >= this to determine master schema

        :raises RuntimeError: if we find datatype mismatches between files or between a file and schema state (provided or from previous inc. batch)
        :return: A dict of the JSON schema representing this stream.
        """
        # TODO: could implement a (user-beware) 'lazy' mode that skips schema checking to improve performance
        # TODO: could utilise min_datetime to add a start_date parameter in spec for user
        if self.master_schema is None:
            master_schema = deepcopy(self._schema)

            file_reader = self.fileformatparser_class(self._format)

            processed_files = []
            for file_info in self.get_time_ordered_file_infos():
                # skip this file if it's earlier than min_datetime
                if (min_datetime is not None) and (file_info.last_modified < min_datetime):
                    continue

                storagefile = self.storagefile_class(file_info, self._provider)
                try:
                    with storagefile.open(file_reader.is_binary) as f:
                        this_schema = file_reader.get_inferred_schema(f, file_info)
                        processed_files.append(file_info)
                except OSError:
                    continue

                if this_schema == master_schema:
                    continue  # exact schema match so go to next file

                # creates a superset of columns retaining order of master_schema with any additional columns added to end
                column_superset = list(master_schema.keys()) + [c for c in this_schema.keys() if c not in master_schema.keys()]
                # this compares datatype of every column that the two schemas have in common
                for col in column_superset:
                    if (col in master_schema.keys()) and (col in this_schema.keys()) and (master_schema[col] != this_schema[col]):
                        # If this column exists in a provided schema or schema state, we'll WARN here rather than throw an error.
                        # This is to allow more leniency as we may be able to coerce this datatype mismatch on read according to
                        # provided schema state. Else we're inferring the schema (or at least this column) from scratch, and therefore
                        # we try to choose the broadest type among two if possible
                        broadest_of_types = self._broadest_type(master_schema[col], this_schema[col])
                        type_explicitly_defined = col in self._schema.keys()
                        override_type = broadest_of_types and not type_explicitly_defined
                        if override_type:
                            master_schema[col] = broadest_of_types
                        if override_type or type_explicitly_defined:
                            LOGGER.warn(
                                f"Detected mismatched datatype on column '{col}', in file '{file_info}'. "
                                + f"Should be '{master_schema[col]}', but found '{this_schema[col]}'. "
                                + f"Airbyte will attempt to coerce this to {master_schema[col]} on read."
                            )
                            continue
                        # otherwise throw an error on mismatching datatypes
                        raise S3Exception(
                            processed_files,
                            "Column type mismatch",
                            f"Detected mismatched datatype on column '{col}', in file '{file_info}'. "
                            + f"Should be '{master_schema[col]}', but found '{this_schema[col]}'.",
                            failure_type=FailureType.config_error,
                        )

                # missing columns in this_schema doesn't affect our master_schema, so we don't check for it here

                # add to master_schema any columns from this_schema that aren't already present
                for col, datatype in this_schema.items():
                    if col not in master_schema.keys():
                        master_schema[col] = datatype

            LOGGER.info(f"determined master schema: {master_schema}")
            self.master_schema = master_schema

        return self.master_schema

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Dict[str, Any]]]:
        """
        This builds full-refresh stream_slices regardless of sync_mode param.
        For full refresh, 1 file == 1 stream_slice.
        The structure of a stream slice is [ {file}, ... ].
        In incremental mode, a stream slice may have more than one file so we mirror that format here.
        Incremental stream_slices are implemented in the IncrementalFileStream child class.
        """

        # TODO: this could be optimised via concurrent reads, however we'd lose chronology and need to deal with knock-ons of that
        # we could do this concurrently both full and incremental by running batches in parallel
        # and then incrementing the cursor per each complete batch
        for file_info in self.get_time_ordered_file_infos():
            yield {"files": [{"storage_file": self.storagefile_class(file_info, self._provider)}]}

    def _match_target_schema(self, record: Dict[str, Any], target_columns: List) -> Dict[str, Any]:
        """
        This method handles missing or additional fields in each record, according to the provided target_columns.
        All missing fields are added, with a value of None (null)
        All additional fields are packed into the _ab_additional_properties object column
        We start off with a check to see if we're already lined up to target in order to avoid unnecessary iterations (useful if many columns)

        :param record: json-like representation of a data row {column:value}
        :param target_columns: list of column names to mutate this record into (obtained via self._get_schema_map().keys() as of now)
        :return: mutated record with columns lining up to target_columns
        """
        compare_columns = [c for c in target_columns if c not in [self.ab_last_mod_col, self.ab_file_name_col]]
        # check if we're already matching to avoid unnecessary iteration
        if set(list(record.keys()) + [self.ab_additional_col]) == set(compare_columns):
            record[self.ab_additional_col] = {}
            return record
        # missing columns
        for c in [col for col in compare_columns if col != self.ab_additional_col]:
            if c not in record.keys():
                record[c] = None
        # additional columns
        record[self.ab_additional_col] = {c: deepcopy(record[c]) for c in record.keys() if c not in compare_columns}
        for c in record[self.ab_additional_col]:
            del record[c]

        return record

    def _add_extra_fields_from_map(self, record: Dict[str, Any], extra_map: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Simple method to take a mapping of columns:values and add them to the provided record

        :param record: json-like representation of a data row {column:value}
        :param extra_map: map of additional columns and values to add
        :return: mutated record with additional fields
        """
        for key, value in extra_map.items():
            record[key] = value
        return record

    def _read_from_slice(
        self,
        file_reader: AbstractFileParser,
        stream_slice: Mapping[str, Any],
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Uses provider-relevant StorageFile to open file and then iterates through stream_records() using format-relevant AbstractFileParser.
        Records are mutated on the fly using _match_target_schema() and _add_extra_fields_from_map() to achieve desired final schema.
        Since this is called per stream_slice, this method works for both full_refresh and incremental.
        """
        for file_item in stream_slice["files"]:
            storage_file: StorageFile = file_item["storage_file"]
            try:
                with storage_file.open(file_reader.is_binary) as f:
                    # TODO: make this more efficient than mutating every record one-by-one as they stream
                    for record in file_reader.stream_records(f, storage_file.file_info):
                        schema_matched_record = self._match_target_schema(record, list(self._get_schema_map().keys()))
                        complete_record = self._add_extra_fields_from_map(
                            schema_matched_record,
                            {
                                self.ab_last_mod_col: datetime.strftime(storage_file.last_modified, self.datetime_format_string),
                                self.ab_file_name_col: storage_file.url,
                            },
                        )
                        yield complete_record
            except OSError:
                continue
        LOGGER.info("finished reading a stream slice")

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        The heavy lifting sits in _read_from_slice() which is full refresh / incremental agnostic
        """
        if stream_slice:
            file_reader = self.fileformatparser_class(self._format, self._get_master_schema())
            yield from self._read_from_slice(file_reader, stream_slice)


class IncrementalFileStream(FileStream, ABC):
    # TODO: ideally want to checkpoint after every file or stream slice rather than N records
    state_checkpoint_interval = None
    buffer_days = 3  # keeping track of all files synced in the last N days
    sync_all_files_always = False
    max_history_size = 1000000000

    @property
    def cursor_field(self) -> str:
        """
        :return: The name of the cursor field.
        """
        return self.ab_last_mod_col

    @staticmethod
    def file_in_history(file_info: FileInfo, history: dict) -> bool:
        for slot in history.values():
            if file_info.key in slot:
                return file_info.key in slot
        return False

    def _get_datetime_from_stream_state(self, stream_state: Mapping[str, Any] = None) -> datetime:
        """if no state, we default to 1970-01-01 in order to pick up all files present."""
        if stream_state is not None and self.cursor_field in stream_state.keys():
            return datetime.strptime(stream_state[self.cursor_field], self.datetime_format_string)
        else:
            return datetime.strptime("1970-01-01T00:00:00+0000", self.datetime_format_string)

    def get_updated_history(self, current_stream_state, latest_record_datetime, latest_record, current_parsed_datetime, state_date):
        """
        History is dict which basically groups files by their modified_at date.
        After reading each record we add its file to the history set if it wasn't already there.
        Then we drop from the history set any entries whose key is less than now - buffer_days
        """

        history = current_stream_state.get("history", {})

        file_modification_date = latest_record_datetime.strftime("%Y-%m-%d")

        # add record to history if record modified date in range delta start from state
        if latest_record_datetime.date() + timedelta(days=self.buffer_days) >= state_date:
            history_item = set(history.setdefault(file_modification_date, set()))
            history_item.add(latest_record[self.ab_file_name_col])
            history[file_modification_date] = history_item

        # reset history to new date state
        if current_parsed_datetime.date() != state_date:
            history = {
                date: history[date]
                for date in history
                if datetime.strptime(date, "%Y-%m-%d").date() + timedelta(days=self.buffer_days) >= state_date
            }

        return history

    def size_history_balancer(self, state_dict):
        """
        Delete history if state size limit reached
        """
        history = state_dict["history"]

        if history.__sizeof__() > self.max_history_size:
            self.sync_all_files_always = True
            state_dict.pop("history")

        return state_dict

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Inspects the latest record extracted from the data source and the current state object and return an updated state object.
        In the case where current_stream_state is null, we default to 1970-01-01 in order to pick up all files present.
        We also save the schema into the state here so that we can use it on future incremental batches, allowing for additional/missing columns.

        :param current_stream_state: The stream's current state object
        :param latest_record: The latest record extracted from the stream
        :return: An updated state object
        """
        state_dict: Dict[str, Any] = {}
        current_parsed_datetime = self._get_datetime_from_stream_state(current_stream_state)
        latest_record_datetime = datetime.strptime(
            latest_record.get(self.cursor_field, "1970-01-01T00:00:00+0000"), self.datetime_format_string
        )
        state_dict[self.cursor_field] = datetime.strftime(max(current_parsed_datetime, latest_record_datetime), self.datetime_format_string)

        state_dict["schema"] = self._get_schema_map()

        state_date = self._get_datetime_from_stream_state(state_dict).date()

        if not self.sync_all_files_always:
            state_dict["history"] = self.get_updated_history(
                current_stream_state, latest_record_datetime, latest_record, current_parsed_datetime, state_date
            )

        return self.size_history_balancer(state_dict)

    def need_to_skip_file(self, stream_state, file_info):
        """
        Skip this file if last_mod is earlier than our cursor value from state and already in history
        or skip this file if last_mod plus delta is earlier than our cursor value
        """
        file_in_history_and_last_modified_is_earlier_than_cursor_value = (
            stream_state is not None
            and self.cursor_field in stream_state.keys()
            and file_info.last_modified <= self._get_datetime_from_stream_state(stream_state)
            and self.file_in_history(file_info, stream_state.get("history", {}))
        )

        file_is_not_in_history_and_last_modified_plus_buffer_days_is_earlier_than_cursor_value = file_info.last_modified + timedelta(
            days=self.buffer_days
        ) < self._get_datetime_from_stream_state(stream_state) and not self.file_in_history(file_info, stream_state.get("history", {}))

        return (
            file_in_history_and_last_modified_is_earlier_than_cursor_value
            or file_is_not_in_history_and_last_modified_plus_buffer_days_is_earlier_than_cursor_value
        )

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Dict[str, Any]]]:
        """
        Builds either full_refresh or incremental stream_slices based on sync_mode.
        An incremental stream_slice is a group of all files with the exact same last_modified timestamp.
        This ensures we only update the cursor state to a given timestamp after ALL files with that timestamp have been successfully read.

        Slight nuance: as we iterate through get_time_ordered_file_infos(),
        we yield the stream_slice containing file(s) up to and Excluding the file on the current iteration.
        The stream_slice is then cleared (if we yielded it) and this iteration's file appended to the (next) stream_slice
        """
        if sync_mode == SyncMode.full_refresh:
            yield from super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)

        else:
            # if necessary and present, let's update this object's schema attribute to the schema stored in state
            # TODO: ideally we could do this on __init__ but I'm not sure that's possible without breaking from cdk style implementation
            if self._schema == {} and stream_state is not None and "schema" in stream_state.keys():
                self._schema = stream_state["schema"]

            # logic here is to bundle all files with exact same last modified timestamp together in each slice
            prev_file_last_mod: datetime = None  # init variable to hold previous iterations last modified
            grouped_files_by_time: List[Dict[str, Any]] = []
            for file_info in self.get_time_ordered_file_infos():
                if self.need_to_skip_file(stream_state, file_info):
                    continue

                # check if this file belongs in the next slice, if so yield the current slice before this file
                if (prev_file_last_mod is not None) and (file_info.last_modified != prev_file_last_mod):
                    yield {"files": grouped_files_by_time}
                    grouped_files_by_time.clear()

                # now we either have an empty stream_slice or a stream_slice that this file shares a last modified with, so append it
                grouped_files_by_time.append({"storage_file": self.storagefile_class(file_info, self._provider)})
                # update our prev_file_last_mod to the current one for next iteration
                prev_file_last_mod = file_info.last_modified

            # now yield the final stream_slice. This is required because our loop only yields the slice previous to its current iteration.
            if len(grouped_files_by_time) > 0:
                yield {"files": grouped_files_by_time}
            else:
                # in case we have no files
                yield None

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        The heavy lifting sits in _read_from_slice() which is full refresh / incremental agnostic.
        We override this for incremental so we can pass our minimum datetime from state into _get_master_schema().
        This means we only parse the schema of new files on incremental runs rather than all files in the bucket.
        """
        if stream_slice:
            if sync_mode == SyncMode.full_refresh:
                yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

            else:

                file_reader = self.fileformatparser_class(
                    self._format, self._get_master_schema(self._get_datetime_from_stream_state(stream_state))
                )
                yield from self._read_from_slice(file_reader, stream_slice)
