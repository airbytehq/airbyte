#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_vk_ads import SourceVkAds

if __name__ == "__main__":
    source = SourceVkAds()
    launch(source, sys.argv[1:])
