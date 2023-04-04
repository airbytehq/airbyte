#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_netsuite2 import SourceNetsuite2

if __name__ == "__main__":
    source = SourceNetsuite2()
    launch(source, sys.argv[1:])
