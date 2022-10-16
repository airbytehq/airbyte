#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_persistiq import SourcePersistiq

if __name__ == "__main__":
    source = SourcePersistiq()
    launch(source, sys.argv[1:])
