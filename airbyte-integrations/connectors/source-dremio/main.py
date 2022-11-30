#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dremio import SourceDremio

if __name__ == "__main__":
    source = SourceDremio()
    launch(source, sys.argv[1:])
