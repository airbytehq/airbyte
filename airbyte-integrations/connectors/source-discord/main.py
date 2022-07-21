#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_discord import SourceDiscord

if __name__ == "__main__":
    source = SourceDiscord()
    launch(source, sys.argv[1:])
