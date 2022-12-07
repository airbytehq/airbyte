#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wolt_venue import SourceWoltVenue

if __name__ == "__main__":
    source = SourceWoltVenue()
    launch(source, sys.argv[1:])
