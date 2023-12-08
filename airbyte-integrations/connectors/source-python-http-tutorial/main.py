#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_python_http_tutorial import SourcePythonHttpTutorial

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePythonHttpTutorial()
    launch(source, sys.argv[1:])
