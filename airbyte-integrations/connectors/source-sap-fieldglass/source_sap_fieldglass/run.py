#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sap_fieldglass import SourceSapFieldglass


def run():
    source = SourceSapFieldglass()
    launch(source, sys.argv[1:])
