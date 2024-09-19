#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import time
import traceback

from airbyte_cdk import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteMessageSerializer, AirbyteTraceMessage, TraceType, Type
from orjson import orjson
from source_gcs import Config, Cursor, SourceGCS, SourceGCSStreamReader


def run():
    _args = sys.argv[1:]
    try:
        catalog_path = AirbyteEntrypoint.extract_catalog(_args)
        config_path = AirbyteEntrypoint.extract_config(_args)
        state_path = AirbyteEntrypoint.extract_state(_args)
        source = SourceGCS(
            SourceGCSStreamReader(),
            Config,
            SourceGCS.read_catalog(catalog_path) if catalog_path else None,
            SourceGCS.read_config(config_path) if config_path else None,
            SourceGCS.read_state(state_path) if state_path else None,
            cursor_cls=Cursor,
        )
    except Exception:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=time.time_ns() // 1_000_000,
                            error=AirbyteErrorTraceMessage(
                                message="Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance.",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
    else:
        launch(source, sys.argv[1:])
