#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pennylane import SourcePennylane

if __name__ == "__main__":
    source = SourcePennylane()
    launch(source, sys.argv[1:])
