#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_braze import SourceBraze

if __name__ == "__main__":
    source = SourceBraze()
    launch(source, sys.argv[1:])
