#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_openweather_low_code import SourceOpenweatherLowCode

if __name__ == "__main__":
    source = SourceOpenweatherLowCode()
    launch(source, sys.argv[1:])
