# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceNetsuiteSuiteql


def run() -> None:
    launch(SourceNetsuiteSuiteql(), sys.argv[1:])
