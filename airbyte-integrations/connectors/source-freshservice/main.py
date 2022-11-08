#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_freshservice import SourceFreshservice

if __name__ == "__main__":
    source = SourceFreshservice()
    launch(source, sys.argv[1:])
