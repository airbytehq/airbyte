#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_paypal_transaction import SourcePaypalTransaction

if __name__ == "__main__":
    source = SourcePaypalTransaction()
    launch(source, sys.argv[1:])
