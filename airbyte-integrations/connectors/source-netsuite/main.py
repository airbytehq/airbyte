#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_netsuite import SourceNetsuite

if __name__ == "__main__":
    source = SourceNetsuite()
    launch(source, sys.argv[1:])
