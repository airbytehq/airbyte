#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_klarna import SourceKlarna

if __name__ == "__main__":
    source = SourceKlarna()
    launch(source, sys.argv[1:])
