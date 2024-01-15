#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_ads import SourceGoogleAds
from source_google_ads.config_migrations import MigrateCustomQuery

if __name__ == "__main__":
    source = SourceGoogleAds()
    MigrateCustomQuery.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
