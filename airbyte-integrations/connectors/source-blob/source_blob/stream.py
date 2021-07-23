# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
import json
import concurrent
from operator import itemgetter
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union
from traceback import format_exc
from airbyte_cdk.models.airbyte_protocol import SyncMode
from fnmatch import fnmatch
from boto3 import session as boto3session
from botocore import UNSIGNED
from botocore.config import Config
from .fileclient import FileClient, FileClientS3
from .filereader import FileReaderCsv

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams import Stream


JSON_TYPES = ["string", "number", "integer", "object", "array", "boolean", "null"]


class ConfigurationError(Exception):
    """Client mis-configured"""


class FileStream(Stream, ABC):
    """
    TODO docstring
    """
    format_filereader_map = {
        'csv': FileReaderCsv,
        # 'parquet': FileReaderParquet,
        # etc.
    }
    ab_additional_col = "_airbyte_additional_properties"
    ab_last_mod_col = "_airbyte_source_file_last_modified"
    ab_file_name_col = "_airbyte_source_file_url"
    datetime_format_string = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, dataset_name: str, provider: dict, format: dict, path_patterns: List[str], schema: str = None):
        self.dataset_name = dataset_name
        self._path_patterns = path_patterns
        self._provider = provider
        self._format = format
        self._schema = {}
        if schema:
            self._schema = self._init_schema(schema)
        self.fileclient_cache = None
        self.master_schema = None

    @staticmethod
    def _init_schema(schema: str) -> Mapping[str,str]:
        """TODO: docstring"""
        try:
            py_schema = json.loads(schema)
        except json.decoder.JSONDecodeError as err:
            error_msg = f"Failed to parse schema {repr(err)}\n{schema}\n{format_exc()}"
            raise ConfigurationError(error_msg) from err
        # enforce all keys and values are of type string as required (i.e. no nesting)
        if not all([isinstance(k, str) and isinstance(v, str) for k,v in py_schema.items()]):
            raise ConfigurationError("Invalid schema provided, all column names and datatypes must be in string format")
        # enforce all values (datatypes) are valid JsonSchema datatypes
        if not all([datatype in JSON_TYPES for datatype in py_schema.values()]):
            raise ConfigurationError(f"Invalid schema provided, datatypes must each be one of {JSON_TYPES}")
        
        return py_schema

    @property
    def name(self) -> str:
        return self.dataset_name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    @property
    def filereader_class(self) -> type:
        return self.format_filereader_map[self._format.get("filetype")]

    @property
    @abstractmethod
    def fileclient_class(self) -> type:
        """TODO docstring"""

    @staticmethod
    @abstractmethod
    def filepath_iterator(logger: AirbyteLogger, provider: dict) -> Iterator[str]:
        """
        TODO docstring
        This needs to yield the 'url' to use in FileClient(). This is possibly better described as blob or file path. e.g.
            For AWS: f"s3://{aws_access_key_id}:{aws_secret_access_key}@{self._url}" <- self._url is what we want to yield here
        """

    def pattern_matched_filepath_iterator(self, filepaths:Iterable[str]) -> Iterator[str]:
        """ TODO docstring """
        for filepath in filepaths:
            for path_pattern in self._path_patterns:
                if fnmatch(filepath, path_pattern):
                    yield filepath

    def time_ordered_fileclient_iterator(self) -> Iterable[Tuple[datetime, FileClient]]:
        """TODO docstring"""

        def get_fileclient_with_lastmod(filepath) -> Tuple[datetime, FileClient]:
            fc = self.fileclient_class(filepath, self._provider)
            return (fc.last_modified, fc)

        if self.fileclient_cache is None:
            fileclients = []  # list of tuples (datetime, FileClient) which we'll use to sort
            # use concurrent future threads to parallelise grabbing last_modified from all the files
            # TODO: don't hardcode max_workers like this
            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
                futures = {
                    executor.submit(get_fileclient_with_lastmod, fp): 
                        fp for fp in self.pattern_matched_filepath_iterator(self.filepath_iterator(self.logger, self._provider))
                }
                for future in concurrent.futures.as_completed(futures):
                    fileclients.append(future.result())  # this will failfast on any errors

            self.fileclient_cache = sorted(fileclients, key=itemgetter(0))

        return self.fileclient_cache

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        TODO docstring
        """
        if self._schema != {}:
            return_schema = deepcopy(self._schema)
        else:  # we have no provided schema or schema state from a previous incremental run
            return_schema = self._get_master_schema()

        return_schema[self.ab_additional_col] = "object"
        return_schema[self.ab_last_mod_col] = "string"
        return_schema[self.ab_file_name_col] = "string"
        return return_schema

    def _get_master_schema(self):
        """ TODO docstring """
        # TODO: maybe implement a 'lazy' mode that skips schema checking to improve performance (user beware)
        if self.master_schema is None:
            master_schema = deepcopy(self._schema)

            file_reader = self.filereader_class(self._format)
            # time order isn't necessary here but we might as well use this method so we cache the list for later use
            for _, fileclient in self.time_ordered_fileclient_iterator():
                with fileclient.open(file_reader.is_binary) as f:
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
                            self.logger.warn(f"Detected mismatched datatype on column '{col}', in file '{fileclient._url}'. "
                                             + f"Should be '{master_schema[col]}', but found '{this_schema[col]}'. "
                                             + f"Airbyte will attempt to coerce this to {master_schema[col]} on read.")
                        # else we're inferring the schema (or at least this column) from scratch and therefore throw an error on mismatching datatypes
                        else:
                            raise RuntimeError(
                                f"Detected mismatched datatype on column '{col}', in file '{fileclient._url}'. "
                                + f"Should be '{master_schema[col]}', but found '{this_schema[col]}'."
                            )

                # missing columns in this_schema doesn't affect our master_schema so we don't check for it here

                # add to master_schema any columns from this_schema that aren't already present
                for col, datatype in this_schema.items():
                    if col not in master_schema.keys():
                        master_schema[col] = datatype

            self.logger.info(f"determined master schema: {master_schema}")
            self.master_schema = master_schema

        return self.master_schema

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        TODO docstring
        This enacts full_refresh style regardless of sync_mode, incremental achieved via incremental child classes
        """
        # TODO: this could be optimised via concurrent reads, however we'd lose chronology and need to deal with knock-ons of that
        # we could do this concurrently both full and incremental by running batches in parallel
        # and then incrementing the cursor per each complete batch
        for last_mod, fileclient in self.time_ordered_fileclient_iterator():
            yield [{
                "unique_url": fileclient._url,
                "last_modified": last_mod,
                "fileclient": fileclient
            }]

    def _match_target_schema(self, record: Mapping[str, Any], target_columns: List) -> Mapping[str, Any]:
        """TODO docstring"""
        # check if we're already matching to avoid unnecessary iteration
        if set(list(record.keys()) + [self.ab_additional_col]) == set(target_columns):
            record[self.ab_additional_col] = {}
            return record
        # missing columns
        for c in [col for col in target_columns if col != self.ab_additional_col]:
            if c not in record.keys():
                record[c] = None
        # additional columns
        record[self.ab_additional_col] = {c: deepcopy(record[c]) for c in record.keys() if c not in target_columns}
        for c in record[self.ab_additional_col].keys():
            del record[c]

        return record

    def _add_extra_fields_from_map(self, record: Mapping[str, Any], extra_map: Mapping[str, Any]) -> Mapping[str, Any]:
        """TODO docstring"""
        for key, value in extra_map.items():
            record[key] = value
        return record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        TODO docstring
        """
        file_reader = self.filereader_class(self._format, self._get_master_schema())

        # TODO: read all files in a stream_slice concurrently
        for file_info in stream_slice:
            with file_info['fileclient'].open(file_reader.is_binary) as f:
                # TODO: make this more efficient than mutating every record one-by-one as they stream
                for record in file_reader.stream_records(f):
                    schema_matched_record = self._match_target_schema(record, list(self.get_json_schema().keys()))
                    complete_record = self._add_extra_fields_from_map(
                        schema_matched_record,
                        {self.ab_last_mod_col: datetime.strftime(file_info['last_modified'], self.datetime_format_string),
                         self.ab_file_name_col: file_info['unique_url']})
                    yield complete_record
        self.logger.info("finished reading a stream slice")


class IncrementalFileStream(FileStream, ABC):
    """
    TODO docstring
    """

    # TODO: ideally want to checkpoint after every file or stream slice rather than N records
    state_checkpoint_interval = None

    # TODO: would be great if we could override time_ordered_fileclient_iterator() here with state awareness
    # this would allow filtering down to only files we need early and avoid unnecessary work

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return self.ab_last_mod_col

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to extract state from the latest record. Needed to implement incremental sync.

        Inspects the latest record extracted from the data source and the current state object and return an updated state object.

        For example: if the state object is based on created_at timestamp, and the current state is {'created_at': 10}, and the latest_record is
        {'name': 'octavia', 'created_at': 20 } then this method would return {'created_at': 20} to indicate state should be updated to this object.

        :param current_stream_state: The stream's current state object
        :param latest_record: The latest record extracted from the stream
        :return: An updated state object
        """
        state_dict = {}
        if current_stream_state is not None and self.cursor_field in current_stream_state.keys():
            current_parsed_datetime = datetime.strptime(current_stream_state[self.cursor_field], self.datetime_format_string)
            latest_record_datetime = datetime.strptime(latest_record[self.cursor_field], self.datetime_format_string)
            state_dict[self.cursor_field] = datetime.strftime(max(current_parsed_datetime, latest_record_datetime), self.datetime_format_string)
        else:
            state_dict[self.cursor_field] = "1970-01-01T00:00:00+0000"

        state_dict["schema"] = self.get_json_schema()
        return state_dict

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        TODO docstring
        """
        if sync_mode.value == "full_refresh":
            yield from super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)

        else:
            # if necessary and present, let's update this object's schema attribute to the schema stored in state
            # TODO: ideally we could do this on __init__ but I'm not sure that's possible without breaking from cdk style implementation
            if self._schema == {} and stream_state is not None and "schema" in stream_state.keys():
                self._schema = stream_state['schema']

            # logic here is to bundle all files with exact same last modified timestamp together in each slice
            prev_file_last_mod = None  # init variable to hold previous iterations last modified
            stream_slice = []

            for last_mod, fileclient in self.time_ordered_fileclient_iterator():
                # skip this file if not needed in this incremental
                if (
                    stream_state is not None
                    and self.cursor_field in stream_state.keys()
                    and last_mod <= datetime.strptime(stream_state[self.cursor_field], self.datetime_format_string)
                ):
                    continue

                # check if this fileclient belongs in the next slice, if so yield the current slice before this file
                if (prev_file_last_mod is not None) and (last_mod != prev_file_last_mod):
                    yield stream_slice
                    stream_slice.clear()
                # now we either have an empty stream_slice or a stream_slice that this file shares a last modified with, so append it
                stream_slice.append({
                    "unique_url": fileclient._url,
                    "last_modified": last_mod,
                    "fileclient": fileclient
                })
                # update our prev_file_last_mod to the current one for next iteration
                prev_file_last_mod = last_mod

            # now yield the final stream_slice. This is required because our loop only yields the slice previous to its current iteration.
            if len(stream_slice) > 0:
                yield stream_slice


class IncrementalFileStreamS3(IncrementalFileStream):
    """TODO docstring"""

    @property
    def fileclient_class(self) -> type:
        return FileClientS3

    @staticmethod
    def _list_bucket(provider:Mapping[str,Any], prefix: str='', accept_key=lambda k: True) -> Iterator[str]:
        """[summary]

        :param provider: [description]
        :type provider: Mapping[str,Any]
        :param prefix: [description], defaults to ''
        :type prefix: str, optional
        :param accept_key: [description], defaults to lambda k:True
        :type accept_key: [type], optional
        :yield: [description]
        :rtype: Iterator[str]
        """
        if FileClientS3.use_aws_account(provider):
            session = boto3session.Session(aws_access_key_id=provider["aws_access_key_id"], aws_secret_access_key=provider["aws_secret_access_key"])
            client = session.client('s3')
        else:
            session = boto3session.Session()
            client = session.client('s3', config=Config(signature_version=UNSIGNED))
        
        ctoken = None
        while True:
            # list_objects_v2 doesn't like a None value for ContinuationToken
            # so we don't set it if we don't have one.
            if ctoken:
                kwargs = dict(Bucket=provider['bucket'], Prefix=prefix, ContinuationToken=ctoken)
            else:
                kwargs = dict(Bucket=provider['bucket'], Prefix=prefix)
            response = client.list_objects_v2(**kwargs)
            try:
                content = response['Contents']
            except KeyError:
                pass
            else:
                for c in content:
                    key = c['Key']
                    if accept_key(key):
                        yield key
            ctoken = response.get('NextContinuationToken', None)
            if not ctoken:
                break

    @staticmethod
    def filepath_iterator(logger: AirbyteLogger, provider: dict) -> Tuple[bool, Optional[Any]]:

        prefix = provider.get("path_prefix")
        if prefix is None:
            prefix = ""

        msg = f"Iterating S3 bucket '{provider['bucket']}'"
        logger.info(msg + f" with prefix: '{prefix}' " if prefix != "" else msg)

        # TODO: use FileClientS3.use_aws_account to check if we're using public or private bucket
        #   then make this work for public as well
        for blob in IncrementalFileStreamS3._list_bucket(
            provider=provider,
            prefix=prefix,
            accept_key=lambda k: not k.endswith('/') # filter out 'folders', we just want actual blobs
        ): 
            yield blob
