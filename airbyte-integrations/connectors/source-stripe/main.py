#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime

from source_stripe import SourceStripe

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type


def _get_source(args: list[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    try:
        return SourceStripe(SourceStripe.read_catalog(catalog_path) if catalog_path else None)
    except Exception as error:
        print(
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
            ).json(),
        )
        return None


if __name__ == "__main__":
    _args = sys.argv[1:]
    source = _get_source(_args)
    if source:
        launch(source, _args)
