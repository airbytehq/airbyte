#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_applovin import SourceApplovin2

if __name__ == "__main__":
    source = SourceApplovin2()
    launch(source, sys.argv[1:])
