#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_pendo_python import SourcePendoPython

if __name__ == "__main__":
    source = SourcePendoPython()
    launch(source, sys.argv[1:])
