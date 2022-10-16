#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_strava import SourceStrava

if __name__ == "__main__":
    source = SourceStrava()
    launch(source, sys.argv[1:])
