#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_metabase import SourceMetabase


def run():
    source = SourceMetabase()
    launch(source, sys.argv[1:])
