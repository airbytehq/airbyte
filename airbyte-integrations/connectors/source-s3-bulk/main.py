#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type
from source_s3.v4 import Config, Cursor
from source_s3.v4.config import CsvFormat
from airbyte_cdk.sources.file_based.file_types.jsonl_parser import JsonlParser
from source_s3_bulk.stream_reader import SourceS3BulkStreamReader
from source_s3_bulk.source import SourceS3Bulk

# the files are actually CSVs, but we are going to trick our StreamReader to output json of the file location
parsers = {CsvFormat: JsonlParser()}

def get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    try:
        return SourceS3Bulk(SourceS3BulkStreamReader(), Config, catalog_path, cursor_cls=Cursor, parsers=parsers)
    except Exception:
        print(
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    emitted_at=int(datetime.now().timestamp() * 1000),
                    error=AirbyteErrorTraceMessage(
                        message="Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance.",
                        stack_trace=traceback.format_exc(),
                    ),
                ),
            ).json()
        )
        return None


if __name__ == "__main__":
    _args = sys.argv[1:]
    source = get_source(_args)

    if source:
        launch(source, _args)
