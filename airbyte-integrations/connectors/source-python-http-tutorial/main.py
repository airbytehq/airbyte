#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_python_http_tutorial import SourcePythonHttpTutorial

if __name__ == "__main__":
    source = SourcePythonHttpTutorial()
    launch(source, sys.argv[1:])
