#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_bigcommerce import SourceBigcommerce


def run():
    source = SourceBigcommerce()
    launch(source, sys.argv[1:])
