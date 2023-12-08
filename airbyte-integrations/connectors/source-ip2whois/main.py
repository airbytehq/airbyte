#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_ip2whois import SourceIp2whois

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceIp2whois()
    launch(source, sys.argv[1:])
