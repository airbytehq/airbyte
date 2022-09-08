#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_weatherstack import SourceWeatherstack

if __name__ == "__main__":
    source = SourceWeatherstack()
    launch(source, sys.argv[1:])
