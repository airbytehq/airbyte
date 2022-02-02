#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_impact_advertisers_report import SourceImpactAdvertisersReport

if __name__ == "__main__":
    source = SourceImpactAdvertisersReport()
    launch(source, sys.argv[1:])
