#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_newsdata import SourceNewsdata

if __name__ == "__main__":
    source = SourceNewsdata()
    launch(source, sys.argv[1:])
