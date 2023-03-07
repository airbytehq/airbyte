#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from unittest.mock import MagicMock
from airbyte_cdk.entrypoint import launch
from source_twitter_tweet import SourceTwitterTweet

if __name__ == "__main__":
    source = SourceTwitterTweet()
    launch(source, sys.argv[1:])
