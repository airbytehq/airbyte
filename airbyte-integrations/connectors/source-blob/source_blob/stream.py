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
from datetime import datetime
import json
import concurrent
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union
from traceback import format_exc
from airbyte_cdk.models.airbyte_protocol import SyncMode
from fnmatch import fnmatch
from smart_open.s3 import _list_bucket
from jsonschema import Draft4Validator, SchemaError
from .blobfile import BlobFile, BlobFileS3
from .filereader import FileReaderCsv

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams import Stream


class ConfigurationError(Exception):
    """Client mis-configured"""


class BlobStream(Stream, ABC):
    """
    TODO docstring
    """

    # TODO: is there a better place to persist this mapping?
    format_filereader_map = {
        'csv': FileReaderCsv,
        # 'parquet': FileReaderParquet,
        # etc.
    }

    def __init__(self, dataset_name: str, provider: dict, format: dict, path: str, schema: str = None):
        self.dataset_name = dataset_name
        self._path = path
        self._provider = provider
        self._format = format
        self._schema = {}
        self.logger = AirbyteLogger()
        if schema:
            try:
                self._schema = json.loads(schema)
            except json.decoder.JSONDecodeError as err:
                error_msg = f"Failed to parse schema {repr(err)}\n{schema}\n{format_exc()}"
                self.logger.error(error_msg)
                raise ConfigurationError(error_msg) from err
            try:
                Draft4Validator.check_schema(self._schema)
            except SchemaError as err:
                error_msg = f"Schema is not a valid JSON schema {repr(err)}\n{schema}\n{format_exc()}"
                self.logger.error(error_msg)
                raise ConfigurationError(error_msg) from err
            # TODO: we could still have an 'invalid' schema after this, should we handle that explicitly?

    @property
    @abstractmethod
    def blobfile_class(self) -> str:
        """TODO docstring"""

    @property
    def name(self) -> str:
        return self.dataset_name

    @property
    def filereader_class(self) -> str:
        return self.format_filereader_map[self._format.get("filetype")]

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None  # TODO: do we want to implement something here?

    @staticmethod
    @abstractmethod
    def blob_iterator(logger: AirbyteLogger, provider: dict) -> Iterator[str]:
        """
        TODO docstring
        This needs to yield the 'url' to use in BlobFile(). This is possibly better described as blob or blob path. e.g.
            For AWS: f"{self.storage_scheme}{aws_access_key_id}:{aws_secret_access_key}@{self.url}" <- self.url is what we want to yield here
        """

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.
        """
        if self._schema:
            return self._schema
        else:
            raise NotImplementedError()
            # TODO: Build in ability to determine schema automatically based on all files for this stream
            # could this look different in incremental v.s. non-incremental?

    def pattern_matched_blobs_iterator(self) -> Iterator[str]:
        """ TODO docstring """
        for blob in self.blob_iterator(self.logger, self._provider):
            if fnmatch(blob, self._path):
                yield blob

    def time_ordered_blobfile_iterator(self) -> Iterator[Tuple[datetime, BlobFile]]:
        """TODO docstring"""

        def get_blobfile_with_lastmod(blob) -> Tuple[datetime, BlobFile]:
            bf = self.blobfile_class(blob, self._provider)
            return (bf.last_modified, bf)

        blobfiles = []  # list of tuples (datetime, BlobFile) which we'll use to sort
        # use concurrent future threads to parallelise grabbing last_modified from all the files
        # TODO: don't hardcode max_workers like this
        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
            futures = {executor.submit(get_blobfile_with_lastmod, blob): blob for blob in self.pattern_matched_blobs_iterator()}
            for future in concurrent.futures.as_completed(futures):
                blobfiles.append(future.result())  # this will failfast on any errors

        for last_mod, blobfile in sorted(blobfiles):
            yield (last_mod, blobfile)

    def read_records(self,
                     sync_mode: SyncMode,
                     cursor_field: List[str],
                     stream_slice: Mapping[str, Any],
                     stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        """
        TODO docstring
        This enacts a full_refresh style read_records regardless of sync_mode
        """
        # TODO: this could be optimised via concurrent reads, however we'd lose chronology and need to deal with knock-ons of that
        # TODO: this is very basic first pass, optimise
        file_reader = self.filereader_class(self._format, self.get_json_schema())
        for last_mod, blobfile in self.time_ordered_blobfile_iterator():
            with blobfile.open(file_reader.is_binary) as f:



class IncrementalBlobStream(BlobStream, ABC):
    """
    TODO docstring
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    def read_records(self,
                     sync_mode: SyncMode,
                     cursor_field: List[str],
                     stream_slice: Mapping[str, Any],
                     stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:

        if sync_mode == "full_refresh":
            yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        else:
            # TODO do the code
            # also could possibly handle the first-time incremental snapshot by using super() here
            pass

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class IncrementalBlobStreamS3(IncrementalBlobStream):
    """TODO docstring"""

    @property
    def blobfile_class(self) -> str:
        return BlobFileS3

    @staticmethod
    def blob_iterator(logger: AirbyteLogger, provider: dict) -> Tuple[bool, Optional[Any]]:

        prefix = provider["path_prefix"]
        if prefix is None:
            prefix = ""

        msg = f"Iterating S3 bucket '{provider['bucket']}'"
        logger.info(msg + f" with prefix: '{prefix}' " if prefix != "" else msg)

        # TODO: use BlobFileS3.use_aws_account to check if we're using public or private bucket
        #   then make this work for public as well

        for blob in _list_bucket(bucket_name=provider['bucket'],
                                 aws_access_key_id=provider["aws_access_key_id"],
                                 aws_secret_access_key=provider["aws_secret_access_key"],
                                 prefix=prefix,
                                 accept_key=lambda k: not k.endswith('/')):  # filter out 'folders', we just want actual blobs
            yield blob
