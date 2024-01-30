#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_sell import SourceZendeskSell


def run():
    source = SourceZendeskSell()
    launch(source, sys.argv[1:])
