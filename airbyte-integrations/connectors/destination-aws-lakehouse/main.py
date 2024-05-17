#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_aws_lakehouse import DestinationAwsLakehouse

if __name__ == "__main__":
    DestinationAwsLakehouse().run(sys.argv[1:])
