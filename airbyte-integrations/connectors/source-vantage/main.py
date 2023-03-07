#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_vantage import SourceVantage

if __name__ == "__main__":
    source = SourceVantage()
    launch(source, sys.argv[1:])
