#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gorgias_api import SourceGorgiasApi

if __name__ == "__main__":
    source = SourceGorgiasApi()
    launch(source, sys.argv[1:])
