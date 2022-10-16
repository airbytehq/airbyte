#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_talk import SourceZendeskTalk

if __name__ == "__main__":
    source = SourceZendeskTalk()
    launch(source, sys.argv[1:])
