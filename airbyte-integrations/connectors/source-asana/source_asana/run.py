#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .config_migration import AsanaConfigMigration
from source_asana import SourceAsana


def run():
    source = SourceAsana()
    AsanaConfigMigration.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
