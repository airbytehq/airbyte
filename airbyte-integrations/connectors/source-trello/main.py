#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_trello import SourceTrello

if __name__ == "__main__":
    source = SourceTrello()
    launch(source, sys.argv[1:])
