#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_outreach import SourceOutreach

if __name__ == "__main__":
    source = SourceOutreach()
    launch(source, sys.argv[1:])
