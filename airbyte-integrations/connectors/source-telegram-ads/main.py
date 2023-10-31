#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_telegram_ads import SourceTelegramAds

if __name__ == "__main__":
    source = SourceTelegramAds()
    launch(source, sys.argv[1:])
