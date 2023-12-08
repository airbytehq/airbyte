#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_analytics_v4 import SourceGoogleAnalyticsV4

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleAnalyticsV4()
    launch(source, sys.argv[1:])
