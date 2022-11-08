#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_youtube_analytics import SourceYoutubeAnalytics

if __name__ == "__main__":
    source = SourceYoutubeAnalytics()
    launch(source, sys.argv[1:])
