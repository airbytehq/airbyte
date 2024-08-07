#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mixpanel import SourceMixpanel
from source_mixpanel.config_migrations import MigrateProjectId


def run():
    source = SourceMixpanel()
    MigrateProjectId.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
