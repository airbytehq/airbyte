#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_pypi import SourcePypi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePypi()
    launch(source, sys.argv[1:])
