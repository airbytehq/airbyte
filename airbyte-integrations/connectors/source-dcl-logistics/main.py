#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dcl_logistics import SourceDclLogistics

if __name__ == "__main__":
    source = SourceDclLogistics()
    launch(source, sys.argv[1:])
