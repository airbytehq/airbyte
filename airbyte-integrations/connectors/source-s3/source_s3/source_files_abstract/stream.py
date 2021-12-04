#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import concurrent
import json
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from operator import itemgetter
from traceback import format_exc
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams import Stream
from wcmatch.glob import GLOBSTAR, SPLIT, globmatch

from .formats.csv_parser import CsvParser
from .formats.parquet_parser import ParquetParser

JSON_TYPES = ["string", "number", "integer", "object", "array", "boolean", "null"]

LOGGER = AirbyteLogger()


class ConfigurationError(Exception):
    """Client mis-configured"""


class FileStream(Stream, ABC):
    @property
    def fileformatparser_map(self):
        """Mapping where every key is equal  'filetype' and values are  corresponding  parser classes."""
        return {
            "csv": CsvParser,
            "parquet": ParquetParser,
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
        self._schema = {}
        if schema:
            self._schema = self._parse_user_input_schema(schema)
        self.master_schema = None
        LOGGER.info(f"initialised stream with format: {format}")

    @staticmethod
    def _parse_user_input_schema(schema: str) -> Mapping[str, str]:
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
            py_schema = json.loads(schema)
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
        file_reader = self.fileformatparser_map.get(self._format.get("filetype"))
        if not file_reader:
            raise RuntimeError(
                f"Detected mismatched file format '{filetype}'. Available values: '{list( self.fileformatparser_map.keys())}''."
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
    def filepath_iterator(self) -> Iterator[str]:
        """
        Provider-specific method to iterate through bucket/container/etc. and yield each full filepath.
        This should supply the 'url' to use in StorageFile(). This is possibly better described as blob or file path.
            e.g. for AWS: f"s3://{aws_access_key_id}:{aws_secret_access_key}@{self.url}" <- self.url is what we want to yield here

        :yield: url filepath to use in StorageFile()
        """

    def pattern_matched_filepath_iterator(self, filepaths: Iterable[str]) -> Iterator[str]:
        """
        iterates through iterable filepaths and yields only those filepaths that match user-provided path patterns

        :param filepaths: filepath_iterator(), this is a param rather than method reference in order to unit test this
        :yield: url filepath to use in StorageFile(), if matching on user-provided path patterns
        """
        for filepath in filepaths:
            if globmatch(filepath, self._path_pattern, flags=GLOBSTAR | SPLIT):
                yield filepath

    @lru_cache(maxsize=None)
    def get_time_ordered_filepaths(self) -> Iterable[Tuple[datetime, str]]:
        """
        Iterates through pattern_matched_filepath_iterator(), acquiring last_modified property of each file to return in time ascending order.
        Uses concurrent.futures to thread this asynchronously in order to improve performance when there are many files (network I/O)
        Caches results after first run of method to avoid repeating network calls as this is used more than once

        :return: list in time-ascending order
        """

        def get_storagefile_with_lastmod(filepath: str) -> Tuple[datetime, str]:
            fc = self.storagefile_class(filepath, self._provider)
            return (fc.last_modified, filepath)

        storagefiles = []
        # use concurrent future threads to parallelise grabbing last_modified from all the files
        # TODO: don't hardcode max_workers like this
        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:

            filepath_gen = self.pattern_matched_filepath_iterator(self.filepath_iterator())

            futures = [executor.submit(get_storagefile_with_lastmod, fp) for fp in filepath_gen]

            for future in concurrent.futures.as_completed(futures):
                # this will failfast on any errors
                storagefiles.append(future.result())

        # The array storagefiles contain tuples of (last_modified, filepath), so sort by last_modified
        return sorted(storagefiles, key=itemgetter(0))

    def _get_schema_map(self) -> Mapping[str, Any]:
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
        properties = {
            column: {"type": ["null", typ]} if column not in self.airbyte_columns else {"type": typ}
            for column, typ in self._get_schema_map().items()
        }

        properties[self.ab_last_mod_col]["format"] = "date-time"
        return {"type": "object", "properties": properties}

    def _get_master_schema(self, min_datetime: datetime = None) -> Mapping[str, Any]:
        """
        In order to auto-infer a schema across many files and/or allow for additional properties (columns),
            we need to determine the superset of schemas across all relevant files.
        This method iterates through get_time_ordered_filepaths() obtaining the inferred schema (process implemented per file format),
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

            for last_mod, filepath in self.get_time_ordered_filepaths():
                # skip this file if it's earlier than min_datetime
                if (min_datetime is not None) and (last_mod < min_datetime):
                    continue

                storagefile = self.storagefile_class(filepath, self._provider)
                with storagefile.open(file_reader.is_binary) as f:
                    this_schema = file_reader.get_inferred_schema(f)

                if this_schema == master_schema:
                    continue  # exact schema match so go to next file

                # creates a superset of columns retaining order of master_schema with any additional columns added to end
                column_superset = list(master_schema.keys()) + [c for c in this_schema.keys() if c not in master_schema.keys()]
                # this compares datatype of every column that the two schemas have in common
                for col in column_superset:
                    if (col in master_schema.keys()) and (col in this_schema.keys()) and (master_schema[col] != this_schema[col]):
                        # if this column exists in a provided schema or schema state, we'll WARN here rather than throw an error
                        # this is to allow more leniency as we may be able to coerce this datatype mismatch on read according to provided schema state
                        # if not, then the read will error anyway
                        if col in self._schema.keys():
                            LOGGER.warn(
                                f"Detected mismatched datatype on column '{col}', in file '{storagefile.url}'. "
                                + f"Should be '{master_schema[col]}', but found '{this_schema[col]}'. "
                                + f"Airbyte will attempt to coerce this to {master_schema[col]} on read."
                            )
                        # else we're inferring the schema (or at least this column) from scratch and therefore throw an error on mismatching datatypes
                        else:
                            raise RuntimeError(
                                f"Detected mismatched datatype on column '{col}', in file '{storagefile.url}'. "
                                + f"Should be '{master_schema[col]}', but found '{this_schema[col]}'."
                            )

                # missing columns in this_schema doesn't affect our master_schema so we don't check for it here

                # add to master_schema any columns from this_schema that aren't already present
                for col, datatype in this_schema.items():
                    if col not in master_schema.keys():
                        master_schema[col] = datatype

            LOGGER.info(f"determined master schema: {master_schema}")
            self.master_schema = master_schema

        return self.master_schema

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
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
        for last_mod, filepath in self.get_time_ordered_filepaths():
            storagefile = self.storagefile_class(filepath, self._provider)
            yield [{"unique_url": storagefile.url, "last_modified": last_mod, "storagefile": storagefile}]

    def _match_target_schema(self, record: Mapping[str, Any], target_columns: List) -> Mapping[str, Any]:
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

    def _add_extra_fields_from_map(self, record: Mapping[str, Any], extra_map: Mapping[str, Any]) -> Mapping[str, Any]:
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
        file_reader,
        stream_slice: Mapping[str, Any],
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Uses provider-relevant StorageFile to open file and then iterates through stream_records() using format-relevant AbstractFileParser.
        Records are mutated on the fly using _match_target_schema() and _add_extra_fields_from_map() to achieve desired final schema.
        Since this is called per stream_slice, this method works for both full_refresh and incremental.
        """
        # TODO: read all files in a stream_slice concurrently
        for file_info in stream_slice:
            with file_info["storagefile"].open(file_reader.is_binary) as f:
                # TODO: make this more efficient than mutating every record one-by-one as they stream
                for record in file_reader.stream_records(f):
                    schema_matched_record = self._match_target_schema(record, list(self._get_schema_map().keys()))
                    complete_record = self._add_extra_fields_from_map(
                        schema_matched_record,
                        {
                            self.ab_last_mod_col: datetime.strftime(file_info["last_modified"], self.datetime_format_string),
                            self.ab_file_name_col: file_info["unique_url"],
                        },
                    )
                    yield complete_record
        LOGGER.info("finished reading a stream slice")
        # Always return an empty generator just in case no records were ever yielded
        yield from []

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
        stream_slice = stream_slice if stream_slice is not None else []
        file_reader = self.fileformatparser_class(self._format, self._get_master_schema())

        yield from self._read_from_slice(file_reader, stream_slice)


class IncrementalFileStream(FileStream, ABC):

    # TODO: ideally want to checkpoint after every file or stream slice rather than N records
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        :return: The name of the cursor field.
        """
        return self.ab_last_mod_col

    def _get_datetime_from_stream_state(self, stream_state: Mapping[str, Any] = None) -> datetime:
        """if no state, we default to 1970-01-01 in order to pick up all files present."""
        if stream_state is not None and self.cursor_field in stream_state.keys():
            return datetime.strptime(stream_state[self.cursor_field], self.datetime_format_string)
        else:
            return datetime.strptime("1970-01-01T00:00:00+0000", self.datetime_format_string)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Inspects the latest record extracted from the data source and the current state object and return an updated state object.
        In the case where current_stream_state is null, we default to 1970-01-01 in order to pick up all files present.
        We also save the schema into the state here so that we can use it on future incremental batches, allowing for additional/missing columns.

        :param current_stream_state: The stream's current state object
        :param latest_record: The latest record extracted from the stream
        :return: An updated state object
        """
        state_dict = {}
        current_parsed_datetime = self._get_datetime_from_stream_state(current_stream_state)
        latest_record_datetime = datetime.strptime(
            latest_record.get(self.cursor_field, "1970-01-01T00:00:00+0000"), self.datetime_format_string
        )
        state_dict[self.cursor_field] = datetime.strftime(max(current_parsed_datetime, latest_record_datetime), self.datetime_format_string)

        state_dict["schema"] = self._get_schema_map()
        return state_dict

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Builds either full_refresh or incremental stream_slices based on sync_mode.
        An incremental stream_slice is a group of all files with the exact same last_modified timestamp.
        This ensures we only update the cursor state to a given timestamp after ALL files with that timestamp have been successfully read.

        Slight nuance: as we iterate through get_time_ordered_filepaths(),
        we yield the stream_slice containing file(s) up to and EXcluding the file on the current iteration.
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
            prev_file_last_mod = None  # init variable to hold previous iterations last modified
            stream_slice = []

            for last_mod, filepath in self.get_time_ordered_filepaths():
                # skip this file if last_mod is earlier than our cursor value from state
                if (
                    stream_state is not None
                    and self.cursor_field in stream_state.keys()
                    and last_mod <= self._get_datetime_from_stream_state(stream_state)
                ):
                    continue

                storagefile = self.storagefile_class(filepath, self._provider)
                # check if this storagefile belongs in the next slice, if so yield the current slice before this file
                if (prev_file_last_mod is not None) and (last_mod != prev_file_last_mod):
                    yield stream_slice
                    stream_slice.clear()
                # now we either have an empty stream_slice or a stream_slice that this file shares a last modified with, so append it
                stream_slice.append({"unique_url": storagefile.url, "last_modified": last_mod, "storagefile": storagefile})
                # update our prev_file_last_mod to the current one for next iteration
                prev_file_last_mod = last_mod

            # now yield the final stream_slice. This is required because our loop only yields the slice previous to its current iteration.
            if stream_slice:
                yield stream_slice

            # in case we have no files
            yield from [None]

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
        if sync_mode == SyncMode.full_refresh:
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

        else:
            stream_slice = stream_slice if stream_slice is not None else []
            file_reader = self.fileformatparser_class(
                self._format, self._get_master_schema(self._get_datetime_from_stream_state(stream_state))
            )
            yield from self._read_from_slice(file_reader, stream_slice)
