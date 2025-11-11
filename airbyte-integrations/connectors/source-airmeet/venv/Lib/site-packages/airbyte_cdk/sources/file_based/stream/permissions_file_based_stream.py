#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import traceback
from typing import Any, Dict, Iterable

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.file_based_stream_permissions_reader import (
    AbstractFileBasedStreamPermissionsReader,
)
from airbyte_cdk.sources.file_based.stream import DefaultFileBasedStream
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.streams.core import JsonSchema
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message


class PermissionsFileBasedStream(DefaultFileBasedStream):
    """
    A specialized stream for handling file-based ACL permissions.

    This stream works with the stream_reader to:
    1. Fetch ACL permissions for each file in the source
    2. Transform permissions into a standardized format
    3. Generate records containing permission information

    The stream_reader is responsible for the actual implementation of permission retrieval
    and schema definition, while this class handles the streaming interface.
    """

    def __init__(
        self, stream_permissions_reader: AbstractFileBasedStreamPermissionsReader, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.stream_permissions_reader = stream_permissions_reader

    def _filter_schema_invalid_properties(
        self, configured_catalog_json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self.stream_permissions_reader.file_permissions_schema

    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[AirbyteMessage]:
        """
        Yield permissions records from all remote files
        """

        for file in stream_slice["files"]:
            no_permissions = False
            file_datetime_string = file.last_modified.strftime(self.DATE_TIME_FORMAT)
            try:
                permissions_record = self.stream_permissions_reader.get_file_acl_permissions(
                    file, logger=self.logger
                )
                if not permissions_record:
                    no_permissions = True
                    self.logger.warning(
                        f"Unable to fetch permissions. stream={self.name} file={file.uri}"
                    )
                    continue
                permissions_record = self.transform_record(
                    permissions_record, file, file_datetime_string
                )
                yield stream_data_to_airbyte_message(self.name, permissions_record)
            except Exception as e:
                self.logger.error(f"Failed to retrieve permissions for file {file.uri}: {str(e)}")
                yield AirbyteMessage(
                    type=MessageType.LOG,
                    log=AirbyteLogMessage(
                        level=Level.ERROR,
                        message=f"Error retrieving files permissions: stream={self.name} file={file.uri}",
                        stack_trace=traceback.format_exc(),
                    ),
                )
            finally:
                if no_permissions:
                    yield AirbyteMessage(
                        type=MessageType.LOG,
                        log=AirbyteLogMessage(
                            level=Level.WARN,
                            message=f"Unable to fetch permissions. stream={self.name} file={file.uri}",
                        ),
                    )

    def _get_raw_json_schema(self) -> JsonSchema:
        """
        Retrieve the raw JSON schema for file permissions from the stream reader.

        Returns:
           The file permissions schema that defines the structure of permission records
        """
        return self.stream_permissions_reader.file_permissions_schema
