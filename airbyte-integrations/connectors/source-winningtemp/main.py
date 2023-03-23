#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_winningtemp import SourceWinningtemp

if __name__ == "__main__":
    source = SourceWinningtemp()
    launch(source, sys.argv[1:])
