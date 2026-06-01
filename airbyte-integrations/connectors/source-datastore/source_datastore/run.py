#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_datastore import SourceDatastore


def run():
    source = SourceDatastore()
    launch(source, sys.argv[1:])
