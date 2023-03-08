#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tiny import SourceTiny

if __name__ == "__main__":
    source = SourceTiny()
    launch(source, sys.argv[1:])
