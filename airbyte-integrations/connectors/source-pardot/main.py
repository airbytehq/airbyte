#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_pardot import SourcePardot

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePardot()
    launch(source, sys.argv[1:])
