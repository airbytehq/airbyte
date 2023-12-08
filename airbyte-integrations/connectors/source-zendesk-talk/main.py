#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zendesk_talk import SourceZendeskTalk

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZendeskTalk()
    launch(source, sys.argv[1:])
