#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_talkdesk_explore import SourceTalkdeskExplore


def run():
    source = SourceTalkdeskExplore()
    launch(source, sys.argv[1:])
