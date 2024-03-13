#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_qualtrics import SourceQualtrics

if __name__ == "__main__":
    source = SourceQualtrics()
    launch(source, sys.argv[1:])
