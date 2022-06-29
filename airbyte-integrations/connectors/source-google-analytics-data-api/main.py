#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_analytics_data_api import SourceGoogleAnalyticsDataApi

if __name__ == "__main__":
    source = SourceGoogleAnalyticsDataApi()
    launch(source, sys.argv[1:])
