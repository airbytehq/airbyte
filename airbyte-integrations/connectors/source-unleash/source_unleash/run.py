#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_unleash import SourceUnleash


def run():
    source = SourceUnleash()
    launch(source, sys.argv[1:])
