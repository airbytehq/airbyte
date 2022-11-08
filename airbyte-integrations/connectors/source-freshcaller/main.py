#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_freshcaller import SourceFreshcaller

if __name__ == "__main__":
    source = SourceFreshcaller()
    launch(source, sys.argv[1:])
