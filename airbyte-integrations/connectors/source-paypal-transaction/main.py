#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_paypal_transaction import SourcePaypalTransaction

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePaypalTransaction()
    launch(source, sys.argv[1:])
