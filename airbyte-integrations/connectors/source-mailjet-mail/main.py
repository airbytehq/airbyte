#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_mailjet_mail import SourceMailjetMail

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceMailjetMail()
    launch(source, sys.argv[1:])
