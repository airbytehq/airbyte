#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_heron_data import SourceHeronData

if __name__ == "__main__":
    source = SourceHeronData()
    launch(source, sys.argv[1:])
