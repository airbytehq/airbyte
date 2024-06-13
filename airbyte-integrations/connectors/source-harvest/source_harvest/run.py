#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_harvest import SourceHarvest

from .config_migrations import MigrateAuthType


def run():
    source = SourceHarvest()
    MigrateAuthType.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
