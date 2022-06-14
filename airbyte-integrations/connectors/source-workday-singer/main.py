#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from source_workday_singer import SourceWorkdaySinger

if __name__ == "__main__":
    source = SourceWorkdaySinger()
    launch(source, sys.argv[1:])
