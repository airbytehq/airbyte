#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_direct_ads import SourceYandexDirectAds


def main():
    source = SourceYandexDirectAds()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    main()
