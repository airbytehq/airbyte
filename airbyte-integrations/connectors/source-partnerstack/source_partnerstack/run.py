#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_partnerstack import SourcePartnerstack


def run():
    source = SourcePartnerstack()
    launch(source, sys.argv[1:])
