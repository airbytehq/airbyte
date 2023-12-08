#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_rd_station_marketing import SourceRDStationMarketing

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceRDStationMarketing()
    launch(source, sys.argv[1:])
