#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import traceback
from typing import List, Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.exceptions import CheckAvailabilityError, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class DefaultFileBasedAvailabilityStrategy(AvailabilityStrategy):
    def __init__(self, stream_reader: AbstractFileBasedStreamReader):
        self.stream_reader = stream_reader

    def check_availability(
        self, stream: AbstractFileBasedStream, logger: logging.Logger, _: Optional[Source]
    ) -> Tuple[bool, Optional[str]]:
        """
        Perform a connection check for the stream.

        Returns (True, None) if successful, otherwise (False, <error message>).

        For the stream:
        - Verify that we can list files from the stream using the configured globs.
        - Verify that we can read one file from the stream.

        This method will also check that the files and their contents are consistent
        with the configured options, as follows:
        - If the files have extensions, verify that they don't disagree with the
          configured file type.
        - If the user provided a schema in the config, check that a subset of records in
          one file conform to the schema via a call to stream.conforms_to_schema(schema).
        """
        try:
            files = self._check_list_files(stream)
            self._check_parse_record(stream, files[0])
        except CheckAvailabilityError as exc:
            tb = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
            return False, "".join(tb)

        return True, None

    def _check_list_files(self, stream: AbstractFileBasedStream) -> List[RemoteFile]:
        try:
            files = stream.list_files()
        except Exception as exc:
            raise CheckAvailabilityError(FileBasedSourceError.ERROR_LISTING_FILES, stream=stream.name) from exc

        if not files:
            raise CheckAvailabilityError(FileBasedSourceError.EMPTY_STREAM, stream=stream.name)

        if not all(f.extension_agrees_with_file_type() for f in files):
            raise CheckAvailabilityError(FileBasedSourceError.EXTENSION_MISMATCH, stream=stream.name)

        return files

    def _check_parse_record(self, stream: AbstractFileBasedStream, file: RemoteFile):
        parser = stream.get_parser(stream.config.file_type)

        try:
            record = next(iter(parser.parse_records(file, self.stream_reader)))
        except StopIteration:
            # The file is empty. We've verified that we can open it, so will
            # consider the connection check successful even though it means
            # we skip the schema validation check.
            return
        except Exception as exc:
            raise CheckAvailabilityError(FileBasedSourceError.ERROR_READING_FILE, stream=stream.name, file=file.uri) from exc

        if stream.config.input_schema:
            if not stream.record_passes_validation_policy(record):
                raise CheckAvailabilityError(
                    FileBasedSourceError.ERROR_VALIDATING_RECORD,
                    stream=stream.name,
                    file=file.uri,
                    validation_policy=stream.config.validation_policy,
                )
