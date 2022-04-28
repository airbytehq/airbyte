#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_all_types import SourceAllTypes

if __name__ == "__main__":
    source = SourceAllTypes()
    launch(source, sys.argv[1:])
