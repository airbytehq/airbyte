#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from facebook_business.api import FacebookAdsApiBatch
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.async_job import InsightAsyncJob, ParentAsyncJob
from source_facebook_marketing.streams.async_job_manager import InsightAsyncJobManager
from source_facebook_marketing.streams.common import JobException


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock()
    api.api.ads_insights_throttle = MyFacebookAdsApi.Throttle(0, 0)
    api.api.new_batch.return_value = mocker.MagicMock(spec=FacebookAdsApiBatch)
    return api


@pytest.fixture(name="time_mock")
def time_mock_fixture(mocker):
    return mocker.patch("source_facebook_marketing.streams.async_job_manager.time")


@pytest.fixture(name="update_job_mock")
def update_job_mock_fixture(mocker):
    return mocker.patch("source_facebook_marketing.streams.async_job_manager.update_in_batch")


class TestInsightAsyncManager:
    def test_jobs_empty(self, api):
        """Should work event without jobs"""
        manager = InsightAsyncJobManager(api=api, jobs=[])
        jobs = list(manager.completed_jobs())
        assert not jobs

    def test_jobs_completed_immediately(self, api, mocker, time_mock):
        """Manager should emmit jobs without waiting if they completed"""
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False),
        ]
        manager = InsightAsyncJobManager(api=api, jobs=jobs)
        completed_jobs = list(manager.completed_jobs())
        assert jobs == completed_jobs
        time_mock.sleep.assert_not_called()

    def test_jobs_wait(self, api, mocker, time_mock, update_job_mock):
        """Manager should return completed jobs and wait for others"""

        def update_job_behaviour():
            jobs[1].completed = True
            yield
            yield
            jobs[0].completed = True
            yield

        update_job_mock.side_effect = update_job_behaviour()
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False),
        ]
        manager = InsightAsyncJobManager(api=api, jobs=jobs)

        job = next(manager.completed_jobs(), None)
        assert job == jobs[1]
        time_mock.sleep.assert_not_called()

        job = next(manager.completed_jobs(), None)
        assert job == jobs[0]
        time_mock.sleep.assert_called_with(InsightAsyncJobManager.JOB_STATUS_UPDATE_SLEEP_SECONDS)

        job = next(manager.completed_jobs(), None)
        assert job is None

    def test_job_restarted(self, api, mocker, time_mock, update_job_mock):
        """Manager should restart failed jobs"""

        def update_job_behaviour():
            jobs[1].failed = True
            yield
            jobs[1].failed = False
            jobs[1].completed = True
            yield

        update_job_mock.side_effect = update_job_behaviour()
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False),
        ]
        manager = InsightAsyncJobManager(api=api, jobs=jobs)

        job = next(manager.completed_jobs(), None)
        assert job == jobs[0]
        jobs[1].restart.assert_called_once()

        job = next(manager.completed_jobs(), None)
        assert job == jobs[1]

        job = next(manager.completed_jobs(), None)
        assert job is None

    def test_job_split(self, api, mocker, time_mock, update_job_mock):
        """Manager should split failed jobs when they fail second time"""

        def update_job_behaviour():
            jobs[1].failed = True
            jobs[1].attempt_number = 2
            yield from range(10)

        update_job_mock.side_effect = update_job_behaviour()
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False),
        ]
        sub_jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
        ]
        sub_jobs[0].get_result.return_value = [1, 2]
        sub_jobs[1].get_result.return_value = [3, 4]
        jobs[1].split_job.return_value = sub_jobs
        manager = InsightAsyncJobManager(api=api, jobs=jobs)

        job = next(manager.completed_jobs(), None)
        assert job == jobs[0]
        jobs[1].split_job.assert_called_once()

        job = next(manager.completed_jobs(), None)
        assert isinstance(job, ParentAsyncJob)
        assert list(job.get_result()) == [1, 2, 3, 4]

        job = next(manager.completed_jobs(), None)
        assert job is None

    def test_job_failed_too_many_times(self, api, mocker, time_mock, update_job_mock):
        """Manager should fail when job failed too many times"""

        def update_job_behaviour():
            jobs[1].failed = True
            jobs[1].attempt_number = InsightAsyncJobManager.MAX_NUMBER_OF_ATTEMPTS
            yield from range(10)

        update_job_mock.side_effect = update_job_behaviour()
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False),
        ]
        manager = InsightAsyncJobManager(api=api, jobs=jobs)

        with pytest.raises(JobException, match=f"{jobs[1]}: failed more than {InsightAsyncJobManager.MAX_NUMBER_OF_ATTEMPTS} times."):
            next(manager.completed_jobs(), None)

    def test_nested_job_failed_too_many_times(self, api, mocker, time_mock, update_job_mock):
        """Manager should fail when a nested job within a ParentAsyncJob failed too many times"""

        def update_job_behaviour():
            jobs[1].failed = True
            sub_jobs[1].failed = True
            sub_jobs[1].attempt_number = InsightAsyncJobManager.MAX_NUMBER_OF_ATTEMPTS
            yield from range(10)

        update_job_mock.side_effect = update_job_behaviour()
        sub_jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False),
        ]
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=True),
            mocker.Mock(spec=ParentAsyncJob, _jobs=sub_jobs, attempt_number=1, failed=False, completed=False),
        ]
        manager = InsightAsyncJobManager(api=api, jobs=jobs)

        with pytest.raises(JobException):
            next(manager.completed_jobs(), None)
