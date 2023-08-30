#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.entrypoint import launch
from source_google_search_console import SourceGoogleSearchConsole
from source_google_search_console.config_migrations import MigrateCustomReports

if __name__ == "__main__":
    source = SourceGoogleSearchConsole()
    # ad-hoc transformation for custom reports backward compatibility
    args = MigrateCustomReports.migrate(source)
    # launch the source with modified config path, if the transformation was applied
    # or launch the source with the original config path, otherwise.
    launch(source, args)
