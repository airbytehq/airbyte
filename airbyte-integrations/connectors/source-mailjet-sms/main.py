#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailjet_sms import SourceMailjetSms

if __name__ == "__main__":
    source = SourceMailjetSms()
    launch(source, sys.argv[1:])
