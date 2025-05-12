#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_sftp import DestinationSftp


if __name__ == "__main__":
    DestinationSftp().run(sys.argv[1:])
