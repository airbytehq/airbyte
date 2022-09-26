#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_metrica import SourceYandexMetrica

if __name__ == "__main__":
    source = SourceYandexMetrica()
    launch(source, sys.argv[1:])
