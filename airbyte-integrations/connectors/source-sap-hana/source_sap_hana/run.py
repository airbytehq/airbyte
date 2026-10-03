# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceSapHana


def run() -> None:
    launch(SourceSapHana(), sys.argv[1:])
