#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_tvmaze_schedule import SourceTvmazeSchedule

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceTvmazeSchedule()
    launch(source, sys.argv[1:])
