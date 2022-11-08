#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_seller_partner import SourceAmazonSellerPartner

if __name__ == "__main__":
    source = SourceAmazonSellerPartner()
    launch(source, sys.argv[1:])
