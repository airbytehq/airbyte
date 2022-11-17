#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_sftp_csv import DestinationSftpCsv

if __name__ == "__main__":
    DestinationSftpCsv().run(sys.argv[1:])
