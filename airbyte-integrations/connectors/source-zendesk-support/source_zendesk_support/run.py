#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_support import SourceZendeskSupport


def run():
    source = SourceZendeskSupport()
    launch(source, sys.argv[1:])
