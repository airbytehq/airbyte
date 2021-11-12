#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from source_facebook_marketing.async_job import AsyncJob
from source_facebook_marketing.api import API
import pytest


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock(spec=API)
    api.account.get_insights.return_value = mocker.MagicMock()
    return api


class TestAsyncJob:
    def test_start(self, api, mocker):
        job = AsyncJob(api=api, params=mocker.MagicMock())
        job.start()

    def test_start_already_started(self, api, mocker):
        job = AsyncJob(api=api, params=mocker.MagicMock())
        job.start()

        with pytest.raises(RuntimeError):
            job.start()

    def test_restart(self, api, mocker):
        job = AsyncJob(api=api, params=mocker.MagicMock())
        job.start()

        # todo: make fail
        job.restart()

        assert job.completed
        assert job.failed

    def test_restart_not_failed(self, api, mocker):
        job = AsyncJob(api=api, params=mocker.MagicMock())
        job.start()

        # todo: make fail
        job.restart()

        assert job.completed
        assert job.failed

    def test_restart_not_started(self, api, mocker):
        job = AsyncJob(api=api, params=mocker.MagicMock())


        with pytest.raises(RuntimeError):
            job.restart()

        assert job.completed
        assert job.failed

    def test_elapsed_time(self):
        pass

    def test_completed(self):
        pass

    def test_failed(self):
        pass

    def test_str(self):
        pass

    def test_get_result(self):
        pass
