#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_analytics_ua import SourceGoogleAnalyticsUA

if __name__ == "__main__":
    source = SourceGoogleAnalyticsUA()
    launch(source, sys.argv[1:])
