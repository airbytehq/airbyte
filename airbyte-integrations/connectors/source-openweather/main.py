#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_openweather import SourceOpenWeather

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceOpenWeather()
    launch(source, sys.argv[1:])
