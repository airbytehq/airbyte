#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_intruder import SourceIntruder

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceIntruder()
    launch(source, sys.argv[1:])
