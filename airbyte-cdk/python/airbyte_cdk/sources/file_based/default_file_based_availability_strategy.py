#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class DefaultFileBasedAvailabilityStrategy(AvailabilityStrategy):
    def __init__(self, stream_reader: AbstractFileBasedStreamReader):
        self.stream_reader = stream_reader

    def check_availability(self, stream: Stream, logger: logging.Logger, _: Optional[Source]) -> Tuple[bool, Optional[str]]:
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
        # TODO: implement this
        return True, None
