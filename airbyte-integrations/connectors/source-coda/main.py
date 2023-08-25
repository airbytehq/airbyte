#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_coda import SourceCoda

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceCoda()
    launch(source, sys.argv[1:])
