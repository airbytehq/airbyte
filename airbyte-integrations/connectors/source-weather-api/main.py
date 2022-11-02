#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_weather_api import SourceWeatherApi

if __name__ == "__main__":
    source = SourceWeatherApi()
    launch(source, sys.argv[1:])
