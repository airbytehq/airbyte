#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_getlago import SourceGetlago


def run():
    source = SourceGetlago()
    launch(source, sys.argv[1:])
