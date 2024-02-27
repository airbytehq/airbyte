#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch
from source_kustomer_singer import SourceKustomerSinger


def run():
    source = SourceKustomerSinger()
    launch(source, sys.argv[1:])
