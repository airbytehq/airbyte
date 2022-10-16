#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hubspot import SourceHubspot

if __name__ == "__main__":
    source = SourceHubspot()
    launch(source, sys.argv[1:])
