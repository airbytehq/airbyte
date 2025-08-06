#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import sys
from airbyte_cdk import launch
from .source import SourceVault


def run() -> None:
    source = SourceVault()
    launch(source, sys.argv[1:])