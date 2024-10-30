#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_chargebee import SourceChargebee


def run():
    source = SourceChargebee()
    launch(source, sys.argv[1:])
