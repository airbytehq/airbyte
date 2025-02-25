#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .config_migrations import MigrateRAASCredentials
from .source import SourceWorkday


def run():
    source = SourceWorkday()
    _args = sys.argv[1:]
    MigrateRAASCredentials.migrate(_args, source)
    launch(source, _args)
