#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_qualaroo import SourceQualaroo


def run():
    source = SourceQualaroo()
    launch(source, sys.argv[1:])
