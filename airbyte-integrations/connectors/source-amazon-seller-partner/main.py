#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_amazon_seller_partner import SourceAmazonSellerPartner

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceAmazonSellerPartner()
    launch(source, sys.argv[1:])
