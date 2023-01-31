#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_market import SourceYandexMarket

if __name__ == "__main__":
    source = SourceYandexMarket()
    launch(source, sys.argv[1:])
