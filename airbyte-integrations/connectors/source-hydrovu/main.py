#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hydrovu import SourceHydrovu

if __name__ == "__main__":
    source = SourceHydrovu()
    launch(source, sys.argv[1:])
