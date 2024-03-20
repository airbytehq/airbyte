#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_ip2whois import SourceIp2whois


def run():
    source = SourceIp2whois()
    launch(source, sys.argv[1:])
