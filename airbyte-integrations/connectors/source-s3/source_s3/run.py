#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from source_s3.v4 import SourceS3


def run() -> None:
    SourceS3.launch()
