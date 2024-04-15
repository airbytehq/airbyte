#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceDealfront

def run():
    source = SourceDealfront()
    launch(source, sys.argv[1:])
