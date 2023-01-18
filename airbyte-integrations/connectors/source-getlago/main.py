#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_getlago import SourceGetlago

if __name__ == "__main__":
    source = SourceGetlago()
    launch(source, sys.argv[1:])
