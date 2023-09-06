#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_search_console import SourceGoogleSearchConsole
from source_google_search_console.config_migrations import MigrateCustomReports

if __name__ == "__main__":
    source = SourceGoogleSearchConsole()
    # migarte config at runtime
    MigrateCustomReports.migrate(sys.argv[1:], source)
    # run the connector
    launch(source, sys.argv[1:])
