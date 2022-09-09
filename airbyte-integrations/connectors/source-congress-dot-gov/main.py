#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_congress_dot_gov import SourceCongressDotGov

if __name__ == "__main__":
    source = SourceCongressDotGov()
    launch(source, sys.argv[1:])
