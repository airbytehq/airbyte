#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zapier_supported_storage import SourceZapierSupportedStorage


def run():
    source = SourceZapierSupportedStorage()
    launch(source, sys.argv[1:])
