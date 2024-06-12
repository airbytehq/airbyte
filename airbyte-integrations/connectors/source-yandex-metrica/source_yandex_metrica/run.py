#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_metrica import SourceYandexMetrica


def run():
    source = SourceYandexMetrica()
    launch(source, sys.argv[1:])
