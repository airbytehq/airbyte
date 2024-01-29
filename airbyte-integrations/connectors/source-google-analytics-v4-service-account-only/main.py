#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_analytics_v4_service_account_only import SourceGoogleAnalyticsV4ServiceAccountOnly

if __name__ == "__main__":
    source = SourceGoogleAnalyticsV4ServiceAccountOnly()
    launch(source, sys.argv[1:])
