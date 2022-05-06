#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_weather import SourceWeather

if __name__ == "__main__":
    source = SourceWeather()
    launch(source, sys.argv[1:])
