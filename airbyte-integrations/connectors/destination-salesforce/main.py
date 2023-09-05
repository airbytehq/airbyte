#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_salesforce import DestinationSalesforce

if __name__ == "__main__":
    DestinationSalesforce().run(sys.argv[1:])
