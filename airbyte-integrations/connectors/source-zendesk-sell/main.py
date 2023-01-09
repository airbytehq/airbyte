#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zendesk_sell import SourceZendeskSell

if __name__ == "__main__":
    source = SourceZendeskSell()
    launch(source, sys.argv[1:])
