#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_customer_io import SourceCustomerIo

if __name__ == "__main__":
    source = SourceCustomerIo()
    launch(source, sys.argv[1:])
