#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailchimp import SourceMailchimp
from source_mailchimp.config_migrations import MigrateDataCenter


def run():
    source = SourceMailchimp()
    MigrateDataCenter.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
