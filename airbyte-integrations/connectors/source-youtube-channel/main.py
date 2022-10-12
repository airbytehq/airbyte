#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_youtube_channel import SourceYoutubeChannel

if __name__ == "__main__":
    source = SourceYoutubeChannel()
    launch(source, sys.argv[1:])
