#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_talkdesk_explore import SourceTalkdeskExplore

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceTalkdeskExplore()
    launch(source, sys.argv[1:])
