#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_analytics_v4 import SourceGoogleAnalyticsV4

if __name__ == "__main__":
    source = SourceGoogleAnalyticsV4()
    launch(source, sys.argv[1:])
