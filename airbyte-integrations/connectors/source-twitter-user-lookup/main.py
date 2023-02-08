#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twitter_user_lookup import SourceTwitterUserLookup

if __name__ == "__main__":
    source = SourceTwitterUserLookup()
    launch(source, sys.argv[1:])
