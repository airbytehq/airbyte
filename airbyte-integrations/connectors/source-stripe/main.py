#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type
from source_stripe import SourceStripe
from ddtrace import config, patch_all, tracer


tracer.configure(hostname="localhost", port=8126, https=False)

config.env = "local"      # the environment the application is in
config.service = "hack-days_source-stripe"  # name of your application
config.version = "0.1"  # version of your application
patch_all()
print("PATCHED_ALL")


def _get_source(args: List[str]):
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
            ).json()
        )
        return None


@tracer.wrap("main", service="hack-days_source-stripe", resource="entrypoint")
def main(args):
    source = _get_source(args)
    if source:
        launch(source, args)


if __name__ == "__main__":
    _args = sys.argv[1:]
    main(_args)
