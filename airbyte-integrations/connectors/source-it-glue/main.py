#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_it_glue import SourceItGlue

if __name__ == "__main__":
    source = SourceItGlue()
    launch(source, sys.argv[1:])
