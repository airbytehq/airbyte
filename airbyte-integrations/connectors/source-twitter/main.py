#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twitter import SourceTwitter

if __name__ == "__main__":
    source = SourceTwitter()
    launch(source, sys.argv[1:])
