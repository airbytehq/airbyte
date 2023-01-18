#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_aha import SourceAha

if __name__ == "__main__":
    source = SourceAha()
    launch(source, sys.argv[1:])
