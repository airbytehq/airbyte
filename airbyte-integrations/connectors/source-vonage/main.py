#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_vonage import SourceVonage

if __name__ == "__main__":
    source = SourceVonage()
    launch(source, sys.argv[1:])
