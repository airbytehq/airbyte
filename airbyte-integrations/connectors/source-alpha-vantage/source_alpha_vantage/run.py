#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_alpha_vantage import SourceAlphaVantage


def run():
    source = SourceAlphaVantage()
    launch(source, sys.argv[1:])
