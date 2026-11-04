#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime
from typing import List, Optional

from orjson import orjson

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch, logger
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteMessageSerializer, AirbyteTraceMessage, TraceType, Type

from .source import SourceAdjust


def _get_source(args: List[str]) -> Optional[SourceAdjust]:
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        return SourceAdjust(
            SourceAdjust.read_catalog(catalog_path) if catalog_path else None,
            SourceAdjust.read_config(config_path) if config_path else None,
            SourceAdjust.read_state(state_path) if state_path else None,
        )
    except Exception as error:
        print(
            orjson.dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=int(datetime.now().timestamp() * 1000),
                            error=AirbyteErrorTraceMessage(
                                message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance. Error: {error}",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
        return None


def run() -> None:
    init_uncaught_exception_handler(logger)
    args = sys.argv[1:]
    source = _get_source(args)
    if source:
        launch(source, args)
