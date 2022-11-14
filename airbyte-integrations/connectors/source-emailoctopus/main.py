#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_emailoctopus import SourceEmailoctopus

if __name__ == "__main__":
    source = SourceEmailoctopus()
    launch(source, sys.argv[1:])
