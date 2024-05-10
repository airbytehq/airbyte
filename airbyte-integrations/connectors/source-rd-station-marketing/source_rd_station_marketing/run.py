#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_rd_station_marketing import SourceRDStationMarketing


def run():
    source = SourceRDStationMarketing()
    launch(source, sys.argv[1:])
