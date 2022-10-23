#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_uk_police import SourceUkPolice

if __name__ == "__main__":
    source = SourceUkPolice()
    launch(source, sys.argv[1:])
