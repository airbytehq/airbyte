#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_slack import SourceSlack
from source_slack.config_migrations import MigrateLegacyConfig


def run():
    source = SourceSlack()
    MigrateLegacyConfig.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
