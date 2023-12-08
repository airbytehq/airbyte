#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_yandex_metrica import SourceYandexMetrica

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceYandexMetrica()
    launch(source, sys.argv[1:])
