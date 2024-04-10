#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_chat import SourceZendeskChat


def run():
    source = SourceZendeskChat()
    launch(source, sys.argv[1:])
