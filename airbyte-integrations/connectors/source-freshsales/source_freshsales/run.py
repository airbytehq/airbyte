#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_freshsales import SourceFreshsales


def run():
    source = SourceFreshsales()
    launch(source, sys.argv[1:])
