#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_huawei_ads import SourceHuaweiAds

if __name__ == "__main__":
    source = SourceHuaweiAds()
    launch(source, sys.argv[1:])
