#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_discourse import SourceDiscourse

if __name__ == "__main__":
    source = SourceDiscourse()
    launch(source, sys.argv[1:])
