#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_jagajam import SourceJagajam

if __name__ == "__main__":
    source = SourceJagajam()
    launch(source, sys.argv[1:])
