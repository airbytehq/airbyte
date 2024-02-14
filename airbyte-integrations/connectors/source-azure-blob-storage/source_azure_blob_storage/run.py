#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
import traceback
from datetime import datetime

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type
from source_azure_blob_storage import Config, SourceAzureBlobStorage, SourceAzureBlobStorageStreamReader


def run():
    args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        source = SourceAzureBlobStorage(
            SourceAzureBlobStorageStreamReader(),
            Config,
            SourceAzureBlobStorage.read_catalog(catalog_path) if catalog_path else None,
            SourceAzureBlobStorage.read_config(config_path) if catalog_path else None,
            SourceAzureBlobStorage.read_state(state_path) if catalog_path else None,
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
    else:
        launch(source, args)
