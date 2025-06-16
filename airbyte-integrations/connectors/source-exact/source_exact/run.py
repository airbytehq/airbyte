# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import sys
import traceback
from datetime import datetime

from orjson import orjson

from airbyte_cdk.entrypoint import launch, logger
from airbyte_cdk.exception_handler import init_uncaught_exception_handler
from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteTraceMessage,
    TraceType,
    Type,
)
from source_exact import SourceExact


def _get_source(_args):
    try:
        return SourceExact()

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
    _args = sys.argv[1:]
    source = _get_source(_args)
    logger.info(f"Running source: {source}")
    if source:
        launch(source, _args)
