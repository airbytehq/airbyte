#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_snapchat_marketing import SourceSnapchatMarketing


def run():
    source = SourceSnapchatMarketing()
    launch(source, sys.argv[1:])
