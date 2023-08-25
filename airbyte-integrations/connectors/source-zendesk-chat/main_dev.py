#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zendesk_chat import SourceZendeskChat

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZendeskChat()
    launch(source, sys.argv[1:])
