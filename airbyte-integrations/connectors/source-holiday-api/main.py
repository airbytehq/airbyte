#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_holiday_api import SourceHolidayApi

if __name__ == "__main__":
    source = SourceHolidayApi()
    launch(source, sys.argv[1:])
