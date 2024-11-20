#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import time
import traceback
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteMessageSerializer, AirbyteTraceMessage, TraceType, Type
from orjson import orjson
from source_klaviyo import SourceKlaviyo


def _get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        return SourceKlaviyo(
            SourceKlaviyo.read_catalog(catalog_path) if catalog_path else None,
            SourceKlaviyo.read_config(config_path) if config_path else None,
            SourceKlaviyo.read_state(state_path) if state_path else None,
        )
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=time.time_ns() // 1_000_000,
                            error=AirbyteErrorTraceMessage(
                                message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance. Error: {error}",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
        raise


def run() -> None:
    args = sys.argv[1:]
    source = _get_source(args)
    launch(source, args)
