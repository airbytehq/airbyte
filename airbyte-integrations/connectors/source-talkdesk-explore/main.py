#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_talkdesk_explore import SourceTalkdeskExplore

if __name__ == "__main__":
    source = SourceTalkdeskExplore()
    launch(source, sys.argv[1:])
