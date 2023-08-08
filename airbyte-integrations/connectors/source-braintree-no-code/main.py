#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_braintree_no_code import SourceBraintreeNoCode

if __name__ == "__main__":
    source = SourceBraintreeNoCode()
    launch(source, sys.argv[1:])
