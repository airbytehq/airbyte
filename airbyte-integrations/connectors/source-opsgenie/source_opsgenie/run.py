#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_opsgenie import SourceOpsgenie


def run():
    source = SourceOpsgenie()
    launch(source, sys.argv[1:])
