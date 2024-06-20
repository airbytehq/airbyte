#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceJinaAiReader

from .config_migration import JinaAiReaderConfigMigration

def run():
    source = SourceJinaAiReader()
    JinaAiReaderConfigMigration.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
