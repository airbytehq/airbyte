#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_google_sheets.client import give_up


@pytest.mark.parametrize(
    "status, need_give_up",
    [
        (429, False), (500, False), (404, True)
    ]
)
def test_give_up(status, need_give_up, mocker):
    e = requests.HTTPError('error')
    e.resp = mocker.Mock(status=status)
    assert need_give_up is give_up(e)
