#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
import copy
import logging
import traceback

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type
from airbyte_cdk.sources.file_based.stream.default_file_based_stream import DefaultFileBasedStream
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.models import SyncMode, ConfiguredAirbyteStream
from airbyte_cdk.sources.file_based.exceptions import (
    DuplicatedFilesError,
    FileBasedSourceError,
    InvalidSchemaError,
    MissingSchemaError,
    RecordParseError,
    SchemaInferenceError,
    StopSyncPerValidationPolicy,
)
from airbyte_cdk.sources.file_based.file_types import FileTransfer
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import (
    SchemaType,
    file_transfer_schema,
    merge_schemas,
    schemaless_schema,
)
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, FailureType, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException



class FlattenableFileBasedStream(DefaultFileBasedStream):
    """
    Extended implementation of DefaultFileBasedStream that supports flattening nested records.
    Specifically used for JSON and JSONL files where records are nested under a specific key.
    """
    
    def __init__(
        self,
        *args,
        flatten_records_key=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.flatten_records_key = flatten_records_key
        # Log that we're using a custom stream with flatten_records_key
        if self.flatten_records_key:
            self.logger.info(f"Stream {self.name}: Using flatten_records_key={self.flatten_records_key}")

    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[Mapping[str, Any] | AirbyteMessage]:
        """
        Override read_records_from_slice to handle flattening of nested records based on the flatten_records_key parameter.
        This method is called by the read_records method and processes records from each slice.
        """
        # If flatten_records_key is not set, use the default implementation
        if not self.flatten_records_key:
            yield from super().read_records_from_slice(stream_slice)
            return
        
        schema = self.catalog_schema
        if schema is None:
            # On read requests we should always have the catalog available
            raise MissingSchemaError(FileBasedSourceError.MISSING_SCHEMA, stream=self.name)
        # The stream only supports a single file type, so we can use the same parser for all files
        parser = self.get_parser()
        for file in stream_slice["files"]:
            # only serialize the datetime once
            file_datetime_string = file.last_modified.strftime(self.DATE_TIME_FORMAT)
            n_skipped = line_no = 0

            try:
                for record in parser.parse_records(
                    self.config, file, self.stream_reader, self.logger, schema
                ):
                    flattened_records = record.get(self.flatten_records_key)
                    for r in flattened_records:
                        line_no += 1
                        data = {"data": r}
                        record = self.transform_record(data, file, file_datetime_string)
                        yield stream_data_to_airbyte_message(self.name, record)
                self._cursor.add_file(file)

            except StopSyncPerValidationPolicy:
                yield AirbyteMessage(
                    type=MessageType.LOG,
                    log=AirbyteLogMessage(
                        level=Level.WARN,
                        message=f"Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema. stream={self.name} file={file.uri} validation_policy={self.config.validation_policy.value} n_skipped={n_skipped}",
                    ),
                )
                break

            except RecordParseError:
                # Increment line_no because the exception was raised before we could increment it
                line_no += 1
                self.errors_collector.collect(
                    AirbyteMessage(
                        type=MessageType.LOG,
                        log=AirbyteLogMessage(
                            level=Level.ERROR,
                            message=f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream={self.name} file={file.uri} line_no={line_no} n_skipped={n_skipped}",
                            stack_trace=traceback.format_exc(),
                        ),
                    ),
                )

            except AirbyteTracedException as exc:
                # Re-raise the exception to stop the whole sync immediately as this is a fatal error
                raise exc

            except Exception:
                yield AirbyteMessage(
                    type=MessageType.LOG,
                    log=AirbyteLogMessage(
                        level=Level.ERROR,
                        message=f"{FileBasedSourceError.ERROR_PARSING_RECORD.value} stream={self.name} file={file.uri} line_no={line_no} n_skipped={n_skipped}",
                        stack_trace=traceback.format_exc(),
                    ),
                )

            finally:
                if n_skipped:
                    yield AirbyteMessage(
                        type=MessageType.LOG,
                        log=AirbyteLogMessage(
                            level=Level.WARN,
                            message=f"Records in file did not pass validation policy. stream={self.name} file={file.uri} n_skipped={n_skipped} validation_policy={self.validation_policy.name}",
                        ),
                    )
