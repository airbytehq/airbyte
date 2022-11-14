#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_ip2whois import SourceIp2whois

if __name__ == "__main__":
    source = SourceIp2whois()
    launch(source, sys.argv[1:])
