#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import sys
import traceback
from datetime import datetime

from airbyte_cdk import AirbyteEntrypoint, AirbyteMessage, Type, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessageSerializer, AirbyteTraceMessage, TraceType
from source_s3.utils import airbyte_message_to_json
from source_s3.v4 import Config, Cursor, SourceS3, SourceS3StreamReader


def get_source(args: list[str]) -> SourceS3 | None:
    # catalog_path = AirbyteEntrypoint.extract_catalog(args)
    # config_path = AirbyteEntrypoint.extract_config(args)
    # state_path = AirbyteEntrypoint.extract_state(args)
    return SourceS3(
        SourceS3StreamReader(),
        Config,
        cursor_cls=Cursor,
        # We will provide these later, when we have proper error handling.
        catalog=None,
        config=None,
        state=None,
        # SourceS3.read_catalog(catalog_path) if catalog_path else None,
        # SourceS3.read_config(config_path) if config_path else None,
        # SourceS3.read_state(state_path) if state_path else None,
    )


def run() -> None:
    _args = sys.argv[1:]
    source: SourceS3 | None = get_source(_args)

    if source:
        launch(source, _args)
