#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from requests.exceptions import HTTPError
from source_airtable.source import SourceAirtable


def test_check_connection_failure(mocker, test_config):
    source = SourceAirtable()
    logger_mock = MagicMock()
    response = source.check_connection(logger_mock, test_config)

    assert response[0] is False
    assert type(response[1]) == HTTPError
