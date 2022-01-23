#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from source_facebook_marketing.streams.async_job_manager import InsightAsyncJobManager


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock()
    api.api.ads_insights_throttle = (0, 0)
    return api


class TestInsightAsyncManager:
    def test_jobs_empty(self, api):
        manager = InsightAsyncJobManager(api=api, jobs=[])
        jobs = list(manager.completed_jobs())
        assert not jobs

    def test_job_restarted(self):
        """TODO"""

    def test_job_split(self):
        """TODO"""

    def test_job_failed_too_many_times(self):
        """TODO"""
