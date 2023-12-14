#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yotpo import SourceYotpo

if __name__ == "__main__":
    source = SourceYotpo()
    launch(source, sys.argv[1:])
