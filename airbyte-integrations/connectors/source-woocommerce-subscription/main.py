#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_woocommerce_subscription import SourceWoocommerceSubscription

if __name__ == "__main__":
    source = SourceWoocommerceSubscription()
    launch(source, sys.argv[1:])
