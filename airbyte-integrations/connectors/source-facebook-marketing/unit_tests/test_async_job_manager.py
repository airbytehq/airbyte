#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from facebook_business.api import FacebookAdsApiBatch
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.async_job import InsightAsyncJob, ParentAsyncJob
from source_facebook_marketing.streams.async_job_manager import APILimit, InsightAsyncJobManager


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
    def test_jobs_empty(self, api, some_config):
        manager = InsightAsyncJobManager(api=api, jobs=[], account_id=some_config["account_ids"][0])
        jobs = list(manager.completed_jobs())
        assert not jobs

    def test_jobs_completed_immediately(self, api, mocker, time_mock, update_job_mock, some_config):
        """
        Manager should emit jobs without waiting if they are already completed.
        (Manager doesn't "restart"; it just yields terminal jobs.)
        """
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, started=True, completed=True, new_jobs=[]),
            mocker.Mock(spec=InsightAsyncJob, started=True, completed=True, new_jobs=[]),
        ]
        # update_in_batch is called but does nothing here
        manager = InsightAsyncJobManager(api=api, jobs=jobs, account_id=some_config["account_ids"][0])

        completed_jobs = list(manager.completed_jobs())
        assert completed_jobs == jobs
        time_mock.sleep.assert_not_called()

    def test_jobs_wait(self, api, mocker, time_mock, update_job_mock, some_config):
        """
        Manager should yield completed jobs and wait for others to complete.
        We'll flip completion flags across sequential polls.
        """
        jobs = [
            mocker.Mock(spec=InsightAsyncJob, started=True, completed=False, new_jobs=[]),
            mocker.Mock(spec=InsightAsyncJob, started=True, completed=False, new_jobs=[]),
        ]

        def side_effect():
            # 1st poll: only jobs[1] becomes completed
            jobs[1].completed = True
            yield
            # 2nd poll: nothing new -> manager must sleep
            yield
            # 3rd poll: jobs[0] becomes completed
            jobs[0].completed = True
            yield

        update_job_mock.side_effect = side_effect()
        manager = InsightAsyncJobManager(api=api, jobs=jobs, account_id=some_config["account_ids"][0])

        it = manager.completed_jobs()

        # First completed job (no waiting yet)
        assert next(it) == jobs[1]
        time_mock.sleep.assert_not_called()

        # Second completed job; during this call the manager should sleep once
        assert next(it) == jobs[0]
        time_mock.sleep.assert_called_with(InsightAsyncJobManager.JOB_STATUS_UPDATE_SLEEP_SECONDS)

        # No more jobs
        assert next(manager.completed_jobs(), None) is None

    def test_new_jobs_are_adopted(self, api, mocker, time_mock, update_job_mock, some_config):
        """
        If a running job emits .new_jobs, the manager should replace it
        with those jobs in the running set, and then yield them when they complete.
        """
        # Parent jobs list: job0 is already completed; job1 will emit children
        job0 = mocker.Mock(spec=InsightAsyncJob, started=True, completed=True, new_jobs=[])
        job1 = mocker.Mock(spec=InsightAsyncJob, started=True, completed=False, new_jobs=[])

        # Children that appear after first poll
        child1 = mocker.Mock(spec=InsightAsyncJob, started=True, completed=True, new_jobs=[])
        child2 = mocker.Mock(spec=InsightAsyncJob, started=True, completed=True, new_jobs=[])

        def side_effect():
            # First poll → job1 emits two children
            job1.new_jobs = [child1, child2]
            yield
            # Second poll → nothing to change; children already terminal
            yield

        update_job_mock.side_effect = side_effect()

        manager = InsightAsyncJobManager(api=api, jobs=[job0, job1], account_id=some_config["account_ids"][0])

        it = manager.completed_jobs()
        # First completed is job0
        assert next(it) == job0
        # Then the two adopted children (order preserved from new_jobs)
        assert next(it) == child1
        assert next(it) == child2
        assert next(manager.completed_jobs(), None) is None

    def test_parent_job_is_emitted_when_provided_as_new_job(self, api, mocker, update_job_mock, some_config):
        """
        If a job emits a ParentAsyncJob in .new_jobs, the manager should adopt it and yield it
        when it's completed (manager doesn't expand or manage children here).
        """
        job = mocker.Mock(spec=InsightAsyncJob, started=True, completed=False, new_jobs=[])
        parent = mocker.Mock(spec=ParentAsyncJob, started=True, completed=True, new_jobs=[])

        def side_effect():
            # On first poll, the job emits a ParentAsyncJob
            job.new_jobs = [parent]
            yield
            # On subsequent polls, nothing new
            yield

        update_job_mock.side_effect = side_effect()
        manager = InsightAsyncJobManager(api=api, jobs=[job], account_id=some_config["account_ids"][0])

        it = manager.completed_jobs()
        # After adoption, the parent is terminal and should be yielded
        assert next(it) == parent
        assert next(manager.completed_jobs(), None) is None


class TestAPILimit:
    def test_refresh_throttle_uses_max_and_pings_account(self, mocker, api):
        # Arrange: per_account=42, per_application=77 -> expect 77
        api.api.ads_insights_throttle = MyFacebookAdsApi.Throttle(42.0, 77.0)
        acct = mocker.Mock()
        api.get_account.return_value = acct

        limit = APILimit(api=api, account_id="act_123")

        limit.refresh_throttle()

        api.get_account.assert_called_once_with(account_id="act_123")
        acct.get_insights.assert_called_once()  # the "ping"
        assert limit.current_throttle == 77.0

    def test_try_consume_success_and_release_accounting(self, mocker, api):
        # Arrange: very low throttle so we never block on throttle
        api.api.ads_insights_throttle = MyFacebookAdsApi.Throttle(0.0, 0.0)
        api.get_account.return_value = mocker.Mock()

        limit = APILimit(api=api, account_id="act_1", throttle_limit=90.0, max_jobs=2)

        # Act / Assert
        assert limit.try_consume() is True
        assert limit.inflight == 1
        assert limit.try_consume() is True
        assert limit.inflight == 2

        # At max_jobs => third should fail even with low throttle
        assert limit.try_consume() is False
        assert limit.inflight == 2

        # Release twice brings inflight back to 0
        limit.release()
        limit.release()
        assert limit.inflight == 0

        # Extra release must not underflow
        limit.release()
        assert limit.inflight == 0

        # refresh_throttle gets called inside try_consume (via get_account().get_insights())
        assert api.get_account.call_count >= 2

    def test_try_consume_blocks_on_throttle(self, mocker, api):
        # Arrange: throttle too high -> block
        api.api.ads_insights_throttle = MyFacebookAdsApi.Throttle(95.0, 10.0)  # max()=95 >= limit
        api.get_account.return_value = mocker.Mock()

        limit = APILimit(api=api, account_id="act_2", throttle_limit=90.0, max_jobs=10)

        # First attempt: blocked by throttle
        assert limit.try_consume() is False
        assert limit.inflight == 0

        # Lower throttle -> allow
        api.api.ads_insights_throttle = MyFacebookAdsApi.Throttle(10.0, 5.0)
        assert limit.try_consume() is True
        assert limit.inflight == 1

    def test_limit_reached_property_works_for_both_conditions(self, api):
        limit = APILimit(api=api, account_id="act_3", throttle_limit=80.0, max_jobs=1)

        # Neither inflight nor throttle blocking
        limit._current_throttle = 0.0
        limit._inflight = 0
        assert limit.limit_reached is False

        # Concurrency cap reached
        limit._inflight = 1
        limit._current_throttle = 0.0
        assert limit.limit_reached is True

        # Throttle cap reached
        limit._inflight = 0
        limit._current_throttle = 80.0
        assert limit.limit_reached is True
