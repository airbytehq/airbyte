#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_assembled import SourceAssembled

if __name__ == "__main__":
    source = SourceAssembled()
    launch(source, sys.argv[1:])
