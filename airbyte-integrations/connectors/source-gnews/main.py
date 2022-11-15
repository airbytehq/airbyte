#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gnews import SourceGnews

if __name__ == "__main__":
    source = SourceGnews()
    launch(source, sys.argv[1:])
