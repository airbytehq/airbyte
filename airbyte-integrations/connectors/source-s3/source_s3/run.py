#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import sys

from airbyte_cdk import launch
from source_s3.v4 import Config, Cursor, SourceS3, SourceS3StreamReader


def get_source(args: list[str] | None = None) -> SourceS3:
    _ = args
    return SourceS3(
        stream_reader=SourceS3StreamReader(),
        spec_class=Config,
        cursor_cls=Cursor,
        # We will provide these later, after we have wrapped proper error handling.
        catalog=None,
        config=None,
        state=None,
    )


def run() -> None:
    launch(
        source=get_source(),
        args=sys.argv[1:],
    )
