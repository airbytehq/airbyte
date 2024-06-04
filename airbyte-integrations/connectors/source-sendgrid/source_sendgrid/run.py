#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sendgrid import SourceSendgrid
from source_sendgrid.config_migrations import MigrateToLowcodeConfig


def run():
    source = SourceSendgrid()
    MigrateToLowcodeConfig.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
