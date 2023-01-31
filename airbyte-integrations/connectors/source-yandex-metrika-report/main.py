#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_metrika_report import SourceYandexMetrikaReport

if __name__ == "__main__":
    source = SourceYandexMetrikaReport()
    launch(source, sys.argv[1:])
