#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_direct import SourceYandexDirect


if __name__ == "__main__":
    source = SourceYandexDirect()
    launch(source, sys.argv[1:])
