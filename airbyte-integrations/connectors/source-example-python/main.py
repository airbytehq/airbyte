#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_example_python import SourceExamplePython

if __name__ == "__main__":
    source = SourceExamplePython()
    launch(source, sys.argv[1:])
