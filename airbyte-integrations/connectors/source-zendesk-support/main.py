#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_support import SourceZendeskSupport

if __name__ == "__main__":
    source = SourceZendeskSupport()
    launch(source, sys.argv[1:])
