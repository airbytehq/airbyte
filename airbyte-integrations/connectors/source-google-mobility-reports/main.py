#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_mobility_reports import SourceGoogleMobilityReports

if __name__ == "__main__":
    source = SourceGoogleMobilityReports()
    launch(source, sys.argv[1:])
