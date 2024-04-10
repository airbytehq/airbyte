#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi
from source_google_analytics_data_api.config_migrations import MigrateCustomReports, MigrateCustomReportsCohortSpec, MigratePropertyID


def run():
    source = SourceGoogleAnalyticsDataApi()
    MigratePropertyID.migrate(sys.argv[1:], source)
    MigrateCustomReports.migrate(sys.argv[1:], source)
    MigrateCustomReportsCohortSpec.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
