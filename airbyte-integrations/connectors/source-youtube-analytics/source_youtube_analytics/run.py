#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_youtube_analytics import SourceYoutubeAnalytics

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceYoutubeAnalytics()
    launch(source, sys.argv[1:])
