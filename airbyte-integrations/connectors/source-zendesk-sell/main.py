#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zendesk_sell import SourceZendeskSell

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZendeskSell()
    launch(source, sys.argv[1:])
