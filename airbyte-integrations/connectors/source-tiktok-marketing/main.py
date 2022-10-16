#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tiktok_marketing import SourceTiktokMarketing

if __name__ == "__main__":
    source = SourceTiktokMarketing()
    launch(source, sys.argv[1:])
