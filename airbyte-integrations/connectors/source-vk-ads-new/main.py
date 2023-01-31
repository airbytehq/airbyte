#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_vk_ads_new import SourceVkAdsNew

if __name__ == "__main__":
    source = SourceVkAdsNew()
    launch(source, sys.argv[1:])
