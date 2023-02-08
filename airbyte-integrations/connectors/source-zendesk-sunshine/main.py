#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_sunshine import SourceZendeskSunshine

if __name__ == "__main__":
    source = SourceZendeskSunshine()
    launch(source, sys.argv[1:])
