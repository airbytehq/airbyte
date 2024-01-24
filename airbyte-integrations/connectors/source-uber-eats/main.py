#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_uber_eats import SourceUberEats

if __name__ == "__main__":
    source = SourceUberEats()
    launch(source, sys.argv[1:])
