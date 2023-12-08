#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_scaffold_source_python import SourceScaffoldSourcePython

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceScaffoldSourcePython()
    launch(source, sys.argv[1:])
