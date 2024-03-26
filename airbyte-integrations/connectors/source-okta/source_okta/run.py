#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceOkta
from .config_migration import OktaConfigMigration

def run():
    source = SourceOkta()
    OktaConfigMigration.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
