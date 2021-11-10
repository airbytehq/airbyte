#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_zendesk_talk import SourceZendeskTalk

if __name__ == "__main__":
    source = SourceZendeskTalk()
    launch(source, sys.argv[1:])
