#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_customer_io import SourceCustomerIo

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceCustomerIo()
    launch(source, sys.argv[1:])
