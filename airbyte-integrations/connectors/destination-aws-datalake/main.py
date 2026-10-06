#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_aws_datalake import DestinationAwsDatalake


if __name__ == "__main__":
    DestinationAwsDatalake().run(sys.argv[1:])
