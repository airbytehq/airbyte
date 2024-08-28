#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tiktok_marketing import SourceTiktokMarketing


def run():
    source = SourceTiktokMarketing()
    launch(source, sys.argv[1:])
