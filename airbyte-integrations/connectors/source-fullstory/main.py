#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_fullstory import SourceFullstory

if __name__ == "__main__":
    source = SourceFullstory()
    launch(source, sys.argv[1:])
