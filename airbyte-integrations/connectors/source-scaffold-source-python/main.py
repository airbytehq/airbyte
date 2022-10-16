#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_scaffold_source_python import SourceScaffoldSourcePython

if __name__ == "__main__":
    source = SourceScaffoldSourcePython()
    launch(source, sys.argv[1:])
