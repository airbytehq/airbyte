"""Entry point for the Tulip source connector."""

import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceTulip


def run():
    source = SourceTulip()
    launch(source, sys.argv[1:])
