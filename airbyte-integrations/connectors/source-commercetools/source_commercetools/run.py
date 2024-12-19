#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_commercetools import SourceCommercetools


def run():
    source = SourceCommercetools()
    launch(source, sys.argv[1:])
