#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twitter_wallet_mapping import SourceTwitterWalletMapping

if __name__ == "__main__":
    source = SourceTwitterWalletMapping()
    launch(source, sys.argv[1:])
