#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_alpha_vantage import SourceAlphaVantage

if __name__ == "__main__":
    source = SourceAlphaVantage()
    launch(source, sys.argv[1:])
