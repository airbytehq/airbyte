#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .config_migrations import MigrateAccountIdToArray, MigrateIncludeDeletedToStatusFilters
from .source import SourceFacebookMarketing


def run():
    source = SourceFacebookMarketing()
    MigrateAccountIdToArray.migrate(sys.argv[1:], source)
    MigrateIncludeDeletedToStatusFilters.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
