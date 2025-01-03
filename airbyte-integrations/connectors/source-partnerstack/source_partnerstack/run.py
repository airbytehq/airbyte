#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_partnerstack import SourcePartnerstack

from airbyte_cdk.entrypoint import launch


def run():
    source = SourcePartnerstack()
    launch(source, sys.argv[1:])
