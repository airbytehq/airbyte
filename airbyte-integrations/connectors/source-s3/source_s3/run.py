#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type
from source_s3.v4 import Config, Cursor, SourceS3, SourceS3StreamReader


def get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        return SourceS3(
            SourceS3StreamReader(),
            Config,
            SourceS3.read_catalog(catalog_path) if catalog_path else None,
            SourceS3.read_config(config_path) if config_path else None,
            SourceS3.read_state(state_path) if state_path else None,
            cursor_cls=Cursor,
        )
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


def run():
    _args = sys.argv[1:]
    source = get_source(_args)

    if source:
        launch(source, _args)
