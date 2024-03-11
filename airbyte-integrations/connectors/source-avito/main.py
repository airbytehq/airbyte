#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_avito import SourceAvito

if __name__ == "__main__":
    source = SourceAvito()
    launch(source, sys.argv[1:])
