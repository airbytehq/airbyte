#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tg_stat import SourceTgStat

if __name__ == "__main__":
    source = SourceTgStat()
    launch(source, sys.argv[1:])
