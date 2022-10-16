#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_asana import SourceAsana

if __name__ == "__main__":
    source = SourceAsana()
    launch(source, sys.argv[1:])
