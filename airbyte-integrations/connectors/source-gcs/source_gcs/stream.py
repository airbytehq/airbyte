# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import traceback
from typing import Any, Iterable

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.file_based.exceptions import (
    FileBasedSourceError,
    MissingSchemaError,
    RecordParseError,
    StopSyncPerValidationPolicy,
)
from airbyte_cdk.sources.file_based.stream import DefaultFileBasedStream
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_gcs.helpers import GCSRemoteFile


class GCSStream(DefaultFileBasedStream):

    """
    Ads transform_record() to base read_records_from_slice().

    """

    def transform_record(self, record: dict[str, Any], file: GCSRemoteFile) -> dict[str, Any]:
        file_datetime_string = file.last_modified.strftime(self.DATE_TIME_FORMAT)

        record[self.ab_last_mod_col] = file_datetime_string
        record[self.ab_file_name_col] = file.displayed_uri if file.displayed_uri else file.uri
        return record

    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[AirbyteMessage]:
        """
        Base implementation from DefaultFileBasedStream.read_records_from_slice
        with providing correct ab_file_name_col value if file has remote_url
        """
        schema = self.catalog_schema
        if schema is None:
            # On read requests we should always have the catalog available
            raise MissingSchemaError(FileBasedSourceError.MISSING_SCHEMA, stream=self.name)
        # The stream only supports a single file type, so we can use the same parser for all files
        parser = self.get_parser()
        for file in stream_slice["files"]:
            # only serialize the datetime once
            n_skipped = line_no = 0

            try:
                for record in parser.parse_records(self.config, file, self.stream_reader, self.logger, schema):
                    line_no += 1
                    if self.config.schemaless:
                        record = {"data": record}
                    elif not self.record_passes_validation_policy(record):
                        n_skipped += 1
                        continue

                    record = self.transform_record(record, file)
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
