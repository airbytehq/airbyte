# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_sftp_json import DestinationSftpJson


def run() -> None:
    DestinationSftpJson().run(sys.argv[1:])


if __name__ == "__main__":
    run()
