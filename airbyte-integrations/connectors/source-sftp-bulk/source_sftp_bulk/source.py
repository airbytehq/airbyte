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

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> tuple[bool, Optional[Any]]:
        """
        WARNING: This is a temporary workaround where we effectively skip the check operation because the memory
        of the footprint for very large file stores.
        :param logger:
        :param config:
        :return:
        """
        return True, None
