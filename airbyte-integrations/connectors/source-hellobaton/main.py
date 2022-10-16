#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hellobaton import SourceHellobaton

if __name__ == "__main__":
    source = SourceHellobaton()
    launch(source, sys.argv[1:])
