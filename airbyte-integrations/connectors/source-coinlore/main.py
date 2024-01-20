#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coinlore import SourceCoinlore

if __name__ == "__main__":
    source = SourceCoinlore()
    launch(source, sys.argv[1:])
