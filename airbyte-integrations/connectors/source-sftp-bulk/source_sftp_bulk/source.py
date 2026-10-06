#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Mapping, Optional

from airbyte_cdk import ConfiguredAirbyteCatalog, TState
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.stream.cursor.default_file_based_cursor import DefaultFileBasedCursor
from source_sftp_bulk.spec import SourceSFTPBulkSpec
from source_sftp_bulk.stream_reader import SourceSFTPBulkStreamReader


logger = logging.getLogger("airbyte")


class SourceSFTPBulk(FileBasedSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: Optional[TState]):
        super().__init__(
            stream_reader=SourceSFTPBulkStreamReader(),
            spec_class=SourceSFTPBulkSpec,
            catalog=catalog,
            config=config,
            state=state,
            cursor_cls=DefaultFileBasedCursor,
        )
