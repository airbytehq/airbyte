#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import pytest
import freezegun


@pytest.fixture()
def mock_sleep(monkeypatch):
    with freezegun.freeze_time(datetime.datetime.now(), ignore=['_pytest.runner', '_pytest.terminal']) as frozen_datetime:
        monkeypatch.setattr('time.sleep', lambda x: frozen_datetime.tick(x))
        yield
