#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_mixpanel import SourceMixpanel
from source_mixpanel.config_migrations import MigrateProjectId

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceMixpanel()
    MigrateProjectId.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
