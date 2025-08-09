#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_commercetools import SourceCommercetools

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceCommercetools()
    launch(source, sys.argv[1:])
