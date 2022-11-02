#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_bored_api import SourceBoredApi

if __name__ == "__main__":
    source = SourceBoredApi()
    launch(source, sys.argv[1:])
