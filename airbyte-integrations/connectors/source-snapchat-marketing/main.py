#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_snapchat_marketing import SourceSnapchatMarketing

if __name__ == "__main__":
    source = SourceSnapchatMarketing()
    launch(source, sys.argv[1:])
