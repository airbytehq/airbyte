#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_analytics_v4_cloud import SourceGoogleAnalyticsV4Cloud

if __name__ == "__main__":
    source = SourceGoogleAnalyticsV4Cloud()
    launch(source, sys.argv[1:])
