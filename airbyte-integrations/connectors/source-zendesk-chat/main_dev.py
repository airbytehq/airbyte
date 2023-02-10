#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_chat import SourceZendeskChat

if __name__ == "__main__":
    source = SourceZendeskChat()
    launch(source, sys.argv[1:])
