#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_cart import SourceCart


def run():
    source = SourceCart()
    launch(source, sys.argv[1:])
