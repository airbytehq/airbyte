#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_outreach import SourceOutreach

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceOutreach()
    launch(source, sys.argv[1:])
