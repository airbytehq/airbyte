#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_talk import SourceZendeskTalk


def run():
    source = SourceZendeskTalk()
    launch(source, sys.argv[1:])
