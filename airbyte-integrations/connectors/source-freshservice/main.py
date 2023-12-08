#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_freshservice import SourceFreshservice

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceFreshservice()
    launch(source, sys.argv[1:])
