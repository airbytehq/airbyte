#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_tiktok_marketing import SourceTiktokMarketing

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceTiktokMarketing()
    launch(source, sys.argv[1:])
