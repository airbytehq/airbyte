#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .config_migration import OktaConfigMigration
from .source import SourceOkta


def run():
    source = SourceOkta()
    OktaConfigMigration.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
