#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime

from airbyte_cdk import AirbyteEntrypoint, AirbyteMessage, Type, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteTraceMessage, TraceType
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from source_azure_blob_storage import SourceAzureBlobStorage, SourceAzureBlobStorageSpec, SourceAzureBlobStorageStreamReader
from source_azure_blob_storage.config_migrations import MigrateCredentials, MigrateLegacyConfig

import sys


class PrintBuffer:
    def __init__(self, buffer_size=1000):
        self.buffer = []
        self.buffer_size = buffer_size

    def write(self, message):
        self.buffer.append(message)
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        if self.buffer:
            # Combine all buffered messages into a single string
            combined_message = "".join(self.buffer)
            # Print combined messages (or handle them in another way)
            sys.__stdout__.write(combined_message + "\n")
            # Clear the buffer
            self.buffer = []

    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()  # Ensure any remaining messages are flushed
        sys.stdout = self.old_stdout


def run():
    print("Init test without buffers")
    args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        sys.stdout = PrintBuffer()
        source = SourceAzureBlobStorage(
            SourceAzureBlobStorageStreamReader(),
            SourceAzureBlobStorageSpec,
            SourceAzureBlobStorage.read_catalog(catalog_path) if catalog_path else None,
            SourceAzureBlobStorage.read_config(config_path) if catalog_path else None,
            SourceAzureBlobStorage.read_state(state_path) if catalog_path else None,
            cursor_cls=DefaultFileBasedCursor,
        )
        MigrateLegacyConfig.migrate(sys.argv[1:], source)
        MigrateCredentials.migrate(sys.argv[1:], source)
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
    finally:
        sys.stdout.flush()
