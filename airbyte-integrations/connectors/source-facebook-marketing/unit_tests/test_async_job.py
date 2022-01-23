#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import time

import pytest
from source_facebook_marketing.api import API
from source_facebook_marketing.streams.async_job import InsightAsyncJob, Status
from source_facebook_marketing.streams.common import JobException


@pytest.fixture(name="adreport")
def adreport_fixture(mocker):
    response = {"report_run_id": 123}
    job = mocker.MagicMock()
    job.__getitem__.side_effect = response.__getitem__
    job.__setitem__.side_effect = response.__setitem__
    job.__iter__.side_effect = response.__iter__
    job.__contains__.side_effect = response.__contains__
    job.api_get.return_value = job
    return job


@pytest.fixture(name="account")
def account_fixture(mocker, adreport):
    account = mocker.Mock()
    account.get_insights.return_value = adreport
    return account


@pytest.fixture(name="job")
def job_fixture(api, account, mocker):
    return InsightAsyncJob(edge_object=account, api=api, params=mocker.MagicMock())


@pytest.fixture(name="failed_job")
def failed_job_fixture(job, adreport):
    adreport["async_status"] = Status.FAILED.value
    adreport["async_percent_completion"] = 0
    job.start()
    job.update_job()

    try:
        _ = job.completed
    except JobException:
        pass

    return job


@pytest.fixture(name="api")
def api_fixture(mocker, adreport):
    api = mocker.Mock(spec=API)

    return api


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
        failed_job.restart()

        assert not failed_job.failed, "restart should reset fail flag"

    def test_restart_when_job_not_failed(self, job, api):
        job.start()
        assert not job.failed

        with pytest.raises(RuntimeError, match=r": Incorrect usage of restart - only failed jobs can be restarted"):
            job.restart()

    def test_restart_when_job_not_started(self, job):
        with pytest.raises(RuntimeError, match=r": Incorrect usage of restart - only failed jobs can be restarted"):
            job.restart()

    def test_elapsed_time(self, job, api, adreport):
        assert job.elapsed_time is None, "should be None for the job that is not started"

        job.start()
        adreport["async_status"] = Status.COMPLETED.value
        adreport["async_percent_completion"] = 0
        job.update_job()

        assert job.elapsed_time, "should be set for the job that is running"

        _ = job.completed
        elapsed_1 = job.elapsed_time
        time.sleep(1)
        elapsed_2 = job.elapsed_time

        assert elapsed_2 == elapsed_1, "should not change after job completed"

    def test_completed_without_start(self, job, api, adreport):
        assert not job.completed
        assert not job.failed

    def test_completed_ok(self, job, api, adreport):
        job.start()
        adreport["async_status"] = Status.COMPLETED.value
        adreport["async_percent_completion"] = 0
        job.update_job()

        assert job.completed, "should return True if the job was completed"
        assert not job.failed, "failed should be set to False"

    def test_completed_failed(self, failed_job, api, adreport):
        assert failed_job.completed
        assert failed_job.failed

    def test_completed_skipped(self, failed_job, api, adreport):
        adreport["async_status"] = Status.SKIPPED.value
        assert failed_job.completed
        assert failed_job.failed

    def test_completed_timeout(self, job, adreport):
        job.start()
        adreport["async_status"] = Status.STARTED.value
        adreport["async_percent_completion"] = 1
        job.update_job()

        assert not job.completed
        assert not job.failed

    def test_completed_timeout_not_started(self, job, adreport):
        job.start()
        adreport["async_status"] = Status.STARTED.value
        adreport["async_percent_completion"] = 0
        assert not job.completed
        assert not job.failed

    def test_failed_no(self, job):
        assert not job.failed, "should return False for active job"

    def test_failed_yes(self, failed_job):
        assert failed_job.failed, "should return True if the job previously failed"

    def test_str(self, api, account):
        job = InsightAsyncJob(edge_object=account, api=api, params={"time_range": 123, "breakdowns": [10, 20]})

        assert str(job) == f"AdReportRun(id=<None>, {account}, time_range=123, breakdowns=[10, 20]"

    def test_get_result(self, job, adreport):
        job.start()

        result = job.get_result()

        adreport.get_result.assert_called_once()
        assert result == adreport.get_result.return_value, "should return result from job"

    def test_get_result_when_job_is_not_started(self, job):
        with pytest.raises(RuntimeError, match=r"Incorrect usage of get_result - the job is not started of failed"):
            job.get_result()

    def test_get_result_when_job_is_failed(self, failed_job):
        with pytest.raises(RuntimeError, match=r"Incorrect usage of get_result - the job is not started of failed"):
            failed_job.get_result()
