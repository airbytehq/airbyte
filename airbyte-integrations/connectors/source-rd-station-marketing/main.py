#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_rd_station_marketing import SourceRDStationMarketing

if __name__ == "__main__":
    source = SourceRDStationMarketing()
    launch(source, sys.argv[1:])
