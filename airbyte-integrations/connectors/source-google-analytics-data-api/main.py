#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleAnalyticsDataApi()
    launch(source, sys.argv[1:])
