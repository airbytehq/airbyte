#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_personio import SourcePersonio

if __name__ == "__main__":
    source = SourcePersonio()
    launch(source, sys.argv[1:])
