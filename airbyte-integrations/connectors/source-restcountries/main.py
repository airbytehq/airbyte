#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_restcountries import SourceRestcountries

if __name__ == "__main__":
    source = SourceRestcountries()
    launch(source, sys.argv[1:])
