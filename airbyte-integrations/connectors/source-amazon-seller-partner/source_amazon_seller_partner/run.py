#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner.config_migrations import MigrateAccountType, MigrateReportOptions, MigrateStreamNameOption


def run():
    source = SourceAmazonSellerPartner()
    MigrateAccountType.migrate(sys.argv[1:], source)
    MigrateReportOptions.migrate(sys.argv[1:], source)
    MigrateStreamNameOption.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
