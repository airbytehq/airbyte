from __future__ import annotations

import sys

from airbyte_cdk import launch

from .source import SourceActiveDirectory


def run() -> None:
    source = SourceActiveDirectory()
    launch(source, sys.argv[1:])