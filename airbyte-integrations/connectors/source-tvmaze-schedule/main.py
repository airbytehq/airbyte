#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tvmaze_schedule import SourceTvmazeSchedule

if __name__ == "__main__":
    source = SourceTvmazeSchedule()
    launch(source, sys.argv[1:])
