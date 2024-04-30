#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_braintree import SourceBraintree


def run():
    source = SourceBraintree()
    launch(source, sys.argv[1:])
