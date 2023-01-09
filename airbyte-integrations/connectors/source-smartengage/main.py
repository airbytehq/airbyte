#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_smartengage import SourceSmartengage

if __name__ == "__main__":
    source = SourceSmartengage()
    launch(source, sys.argv[1:])
