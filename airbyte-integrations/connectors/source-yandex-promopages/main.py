#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_yandex_promopages import SourceYandexPromopages

if __name__ == "__main__":
    source = SourceYandexPromopages()
    launch(source, sys.argv[1:])
