#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.logger import AirbyteLogger
from source_mailchimp import SourceMailchimp


def test_client_wrong_credentials():
    source = SourceMailchimp()
    status, error = source.check_connection(logger=AirbyteLogger, config={"username": "Jonny", "apikey": "blah-blah"})
    assert not status
