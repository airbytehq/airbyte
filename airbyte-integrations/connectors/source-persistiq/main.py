#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_persistiq import SourcePersistiq

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePersistiq()
    launch(source, sys.argv[1:])
