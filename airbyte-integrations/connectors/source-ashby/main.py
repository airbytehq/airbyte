#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_ashby import SourceAshby

if __name__ == "__main__":
    source = SourceAshby()
    launch(source, sys.argv[1:])
