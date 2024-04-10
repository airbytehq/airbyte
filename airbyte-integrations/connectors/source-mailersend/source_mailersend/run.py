#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailersend import SourceMailersend


def run():
    source = SourceMailersend()
    launch(source, sys.argv[1:])
