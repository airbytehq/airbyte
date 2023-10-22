#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type
from airbyte_cdk.sources.file_based.file_types import default_parsers
from source_s3.v4 import Config, Cursor, SourceS3, SourceS3StreamReader
from source_s3.v4.config import UnstructuredFormat
from source_s3.v4.unstructured_parser import UnstructuredParser

parsers = {**default_parsers, UnstructuredFormat: UnstructuredParser()}


def get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    try:
        return SourceS3(SourceS3StreamReader(), Config, catalog_path, cursor_cls=Cursor, parsers=parsers)
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
