#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_mailjet_sms import SourceMailjetSms

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceMailjetSms()
    launch(source, sys.argv[1:])
