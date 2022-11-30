#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_youtube_analytics_business import SourceYoutubeAnalyticsBusiness

if __name__ == "__main__":
    source = SourceYoutubeAnalyticsBusiness()
    launch(source, sys.argv[1:])
