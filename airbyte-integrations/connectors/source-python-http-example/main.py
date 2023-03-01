#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_python_http_example import SourcePythonHttpExample

if __name__ == "__main__":
    source = SourcePythonHttpExample()
    launch(source, sys.argv[1:])
