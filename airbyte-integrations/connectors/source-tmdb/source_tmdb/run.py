#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tmdb import SourceTmdb


def run():
    source = SourceTmdb()
    launch(source, sys.argv[1:])
