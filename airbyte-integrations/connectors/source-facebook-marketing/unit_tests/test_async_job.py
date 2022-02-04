#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import time
from typing import Iterator
from unittest.mock import call

import pendulum
import pytest
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.api import FacebookAdsApiBatch
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.async_job import InsightAsyncJob, ParentAsyncJob, Status, chunks


@pytest.fixture(name="adreport")
def adreport_fixture(mocker, api):
    ao = AdReportRun(fbid=123, api=api)
    ao["report_run_id"] = 123
    mocker.patch.object(AdReportRun, "api_get", return_value=ao)
    mocker.patch.object(AdReportRun, "get_result", return_value={})
    return ao


@pytest.fixture(name="account")
def account_fixture(mocker, adreport):
    account = mocker.Mock()
    account.get_insights.return_value = adreport
    return account


@pytest.fixture(name="job")
def job_fixture(api, account):
    params = {
        "level": "ad",
        "action_breakdowns": [],
        "breakdowns": [],
        "fields": ["field1", "field2"],
        "time_increment": 1,
        "action_attribution_windows": [],
    }
    interval = pendulum.Period(pendulum.Date(2019, 1, 1), pendulum.Date(2019, 1, 1))

    return InsightAsyncJob(edge_object=account, api=api, interval=interval, params=params)


@pytest.fixture(name="grouped_jobs")
def grouped_jobs_fixture(mocker):
    return [mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False) for _ in range(10)]


@pytest.fixture(name="parent_job")
def parent_job_fixture(api, grouped_jobs):
    interval = pendulum.Period(pendulum.Date(2019, 1, 1), pendulum.Date(2019, 1, 1))
    return ParentAsyncJob(api=api, jobs=grouped_jobs, interval=interval)


@pytest.fixture(name="started_job")
def started_job_fixture(job, adreport):
    adreport["async_status"] = Status.RUNNING.value
    adreport["async_percent_completion"] = 0
    job.start()

    return job


@pytest.fixture(name="completed_job")
def completed_job_fixture(started_job, adreport):
    adreport["async_status"] = Status.COMPLETED.value
    adreport["async_percent_completion"] = 100
    started_job.update_job()

    return started_job


@pytest.fixture(name="late_job")
def late_job_fixture(started_job, adreport):
    adreport["async_status"] = Status.COMPLETED.value
    adreport["async_percent_completion"] = 100
    started_job.update_job()

    return started_job


@pytest.fixture(name="failed_job")
def failed_job_fixture(started_job, adreport):
    adreport["async_status"] = Status.FAILED.value
    adreport["async_percent_completion"] = 0
    started_job.update_job()

    return started_job


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock(spec=MyFacebookAdsApi)
    api.call().json.return_value = {}
    api.new_batch().execute.return_value = None  # short-circuit batch execution of failed jobs, prevent endless loop

    return api


class TestChunks:
    def test_two_or_more(self):
        result = chunks([1, 2, 3, 4, 5], 2)

        assert isinstance(result, Iterator), "should be iterator/generator"
        assert list(result) == [[1, 2], [3, 4], [5]]

    def test_single(self):
        result = chunks([1, 2, 3, 4, 5], 6)

        assert isinstance(result, Iterator), "should be iterator/generator"
        assert list(result) == [[1, 2, 3, 4, 5]]


class TestInsightAsyncJob:
    def test_start(self, job):
        job.start()

        assert job._job
        assert job.elapsed_time

    def test_start_already_started(self, job):
        job.start()

        with pytest.raises(RuntimeError, match=r": Incorrect usage of start - the job already started, use restart instead"):
            job.start()

    def test_restart(self, failed_job, api, adreport):
        assert failed_job.attempt_number == 1

        failed_job.restart()

        assert not failed_job.failed, "restart should reset fail flag"
        assert failed_job.attempt_number == 2

    def test_restart_when_job_not_failed(self, job, api):
        job.start()
        assert not job.failed

        with pytest.raises(RuntimeError, match=r": Incorrect usage of restart - only failed jobs can be restarted"):
            job.restart()

    def test_restart_when_job_not_started(self, job):
        with pytest.raises(RuntimeError, match=r": Incorrect usage of restart - only failed jobs can be restarted"):
            job.restart()

    def test_update_job_not_started(self, job):
        with pytest.raises(RuntimeError, match=r": Incorrect usage of the method - the job is not started"):
            job.update_job()

    def test_update_job_on_completed_job(self, completed_job, adreport):
        completed_job.update_job()

        adreport.api_get.assert_called_once()

    def test_update_job(self, started_job, adreport):
        started_job.update_job()

        adreport.api_get.assert_called_once()

    def test_update_job_with_batch(self, started_job, adreport, mocker):
        response = mocker.Mock()

        response.json.return_value = {
            "id": "1128003977936306",
            "account_id": "212551616838260",
            "time_ref": 1642989751,
            "time_completed": 1642989754,
            "async_status": "Job Completed",
            "async_percent_completion": 100,
            "date_start": "2021-02-24",
            "date_stop": "2021-02-24",
        }
        response.body.return_value = "Some error"
        batch_mock = mocker.Mock(spec=FacebookAdsApiBatch)

        started_job.update_job(batch=batch_mock)

        adreport.api_get.assert_called_once()
        args, kwargs = adreport.api_get.call_args
        assert kwargs["batch"] == batch_mock

        kwargs["success"](response)
        assert started_job.completed

        kwargs["failure"](response)

    def test_elapsed_time(self, job, api, adreport):
        assert job.elapsed_time is None, "should be None for the job that is not started"

        job.start()
        adreport["async_status"] = Status.COMPLETED.value
        adreport["async_percent_completion"] = 0
        job.update_job()

        assert job.elapsed_time, "should be set for the job that is running"

        elapsed_1 = job.elapsed_time
        time.sleep(1)
        elapsed_2 = job.elapsed_time

        assert elapsed_2 == elapsed_1, "should not change after job completed"

    def test_completed_without_start(self, job, api, adreport):
        assert not job.completed
        assert not job.failed

    def test_completed_ok(self, completed_job, api, adreport):
        assert completed_job.completed, "should return True if the job was completed"
        assert not completed_job.failed, "failed should be set to False"

    def test_completed_failed(self, failed_job, api, adreport):
        assert failed_job.completed
        assert failed_job.failed

    def test_completed_skipped(self, failed_job, api, adreport):
        adreport["async_status"] = Status.SKIPPED.value
        assert failed_job.completed
        assert failed_job.failed

    def test_failed_no(self, job):
        assert not job.failed, "should return False for active job"

    def test_failed_yes(self, failed_job):
        assert failed_job.failed, "should return True if the job previously failed"

    def test_str(self, api, account):
        interval = pendulum.Period(pendulum.Date(2010, 1, 1), pendulum.Date(2011, 1, 1))
        job = InsightAsyncJob(
            edge_object=account, api=api, params={"breakdowns": [10, 20]}, interval=interval,
        )

        assert str(job) == f"InsightAsyncJob(id=<None>, {account}, time_range=<Period [2010-01-01 -> 2011-01-01]>, breakdowns=[10, 20])"

    def test_get_result(self, job, adreport):
        job.start()

        result = job.get_result()

        adreport.get_result.assert_called_once()
        assert result == adreport.get_result.return_value, "should return result from job"

    def test_get_result_when_job_is_not_started(self, job):
        with pytest.raises(RuntimeError, match=r"Incorrect usage of get_result - the job is not started or failed"):
            job.get_result()

    def test_get_result_when_job_is_failed(self, failed_job):
        with pytest.raises(RuntimeError, match=r"Incorrect usage of get_result - the job is not started or failed"):
            failed_job.get_result()

    def test_split_job(self, job, account, mocker, api):
        account.get_insights.return_value = [{"campaign_id": 1}, {"campaign_id": 2}, {"campaign_id": 3}]
        parent_job_mock = mocker.patch("source_facebook_marketing.streams.async_job.ParentAsyncJob")
        campaign_mock = mocker.patch("source_facebook_marketing.streams.async_job.Campaign")

        parent_job = job.split_job()

        account.get_insights.assert_called_once()
        campaign_mock.assert_has_calls([call(1), call(2), call(3)])
        assert parent_job_mock.called
        assert parent_job
        _args, kwargs = parent_job_mock.call_args
        assert len(kwargs["jobs"]) == 3, "number of jobs should match number of campaigns"


class TestParentAsyncJob:
    def test_start(self, parent_job, grouped_jobs):
        parent_job.start()
        for job in grouped_jobs:
            job.start.assert_called_once()

    def test_restart(self, parent_job, grouped_jobs):
        assert not parent_job.failed, "initially not failed"

        # fail some jobs
        grouped_jobs[0].failed = True
        grouped_jobs[0].attempt_number = 2
        grouped_jobs[5].failed = True
        grouped_jobs[0].attempt_number = 2
        grouped_jobs[6].attempt_number = 3

        assert parent_job.failed, "should be failed if any job failed"
        parent_job.restart()
        assert parent_job.failed
        assert parent_job.attempt_number == 3, "restart should be max value of all jobs"

    def test_completed(self, parent_job, grouped_jobs):
        assert not parent_job.completed, "initially not completed"

        # complete some jobs
        grouped_jobs[0].completed = True
        grouped_jobs[5].completed = True

        assert not parent_job.completed, "not completed until all jobs completed"

        # complete all jobs
        for job in grouped_jobs:
            job.completed = True

        assert parent_job.completed, "completed because all jobs completed"

    def test_update_job(self, parent_job, grouped_jobs, api):
        """Checks jobs status in advance and restart if some failed."""
        # finish some jobs
        grouped_jobs[0].completed = True
        grouped_jobs[5].completed = True

        parent_job.update_job()

        # assert
        batch_mock = api.new_batch()
        for i, job in enumerate(grouped_jobs):
            if i in (0, 5):
                job.update_job.assert_not_called()
            else:
                job.update_job.assert_called_once_with(batch=batch_mock)

    def test_get_result(self, parent_job, grouped_jobs):
        """Retrieve result of the finished job."""
        for job in grouped_jobs:
            job.get_result.return_value = []
        grouped_jobs[0].get_result.return_value = range(3, 8)
        grouped_jobs[6].get_result.return_value = range(4, 11)

        generator = parent_job.get_result()

        assert isinstance(generator, Iterator)
        assert list(generator) == list(range(3, 8)) + list(range(4, 11))

    def test_split_job(self, parent_job):
        with pytest.raises(RuntimeError, match="Splitting of ParentAsyncJob is not allowed."):
            parent_job.split_job()
