#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_datascope import SourceDatascope

if __name__ == "__main__":
    source = SourceDatascope()
    launch(source, sys.argv[1:])
