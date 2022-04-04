#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_redshift_py import DestinationRedshiftPy

if __name__ == "__main__":
    DestinationRedshiftPy().run(sys.argv[1:])
