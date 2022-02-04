#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_sftp_json import DestinationSftpJson

if __name__ == "__main__":
    DestinationSftpJson().run(sys.argv[1:])
