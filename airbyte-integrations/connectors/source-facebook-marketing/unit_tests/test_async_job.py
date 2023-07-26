#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import time
from typing import Iterator

import pendulum
import pytest
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApiBatch, FacebookBadObjectError
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.async_job import InsightAsyncJob, ParentAsyncJob, Status, update_in_batch


@pytest.fixture(name="adreport")
def adreport_fixture(mocker, api):
    ao = AdReportRun(fbid="123", api=api)
    ao["report_run_id"] = "123"
    mocker.patch.object(ao, "api_get", side_effect=ao.api_get)
    mocker.patch.object(ao, "get_result", side_effect=ao.get_result)
    return ao


@pytest.fixture(name="account")
def account_fixture(mocker, adreport):
    account = mocker.Mock(spec=AdAccount)
    account.get_insights.return_value = adreport
    return account


@pytest.fixture(name="job")
def job_fixture(api, account):
    params = {
        "level": "ad",
        "action_breakdowns": [],
        "action_report_time": "mixed",
        "breakdowns": [],
        "fields": ["field1", "field2"],
        "time_increment": 1,
        "action_attribution_windows": [],
    }
    interval = pendulum.Period(pendulum.Date(2019, 1, 1), pendulum.Date(2019, 1, 1))

    return InsightAsyncJob(edge_object=account, api=api, interval=interval, params=params)


@pytest.fixture(name="grouped_jobs")
def grouped_jobs_fixture(mocker):
    return [mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False, elapsed_time=None) for _ in range(10)]


@pytest.fixture(name="parent_job")
def parent_job_fixture(api, grouped_jobs):
    interval = pendulum.Period(pendulum.Date(2019, 1, 1), pendulum.Date(2019, 1, 1))
    return ParentAsyncJob(api=api, jobs=grouped_jobs, interval=interval)


@pytest.fixture(name="started_job")
def started_job_fixture(job, adreport, mocker):
    adreport["async_status"] = Status.RUNNING.value
    adreport["async_percent_completion"] = 0
    mocker.patch.object(job, "update_job", wraps=job.update_job)
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
    api.call().error.return_value = False

    return api


@pytest.fixture(name="batch")
def batch_fixture(api, mocker):
    batch = FacebookAdsApiBatch(api=api)
    mocker.patch.object(batch, "execute", wraps=batch.execute)
    api.new_batch.return_value = batch

    return batch


class TestUpdateInBatch:
    """Test update_in_batch"""

    def test_less_jobs(self, api, started_job, batch):
        """Should update all jobs when number of jobs less than max size of batch"""
        jobs = [started_job for _ in range(49)]

        update_in_batch(api=api, jobs=jobs)

        assert started_job.update_job.call_count == 49
        assert len(api.new_batch.return_value) == 49
        batch.execute.assert_called_once()

    def test_more_jobs(self, api, started_job, batch):
        """Should update all jobs when number of jobs greater than max size of batch"""
        second_batch = copy.deepcopy(batch)
        jobs = [started_job for _ in range(55)]
        api.new_batch.return_value = None
        api.new_batch.side_effect = [batch, second_batch]

        update_in_batch(api=api, jobs=jobs)

        assert started_job.update_job.call_count == 55
        assert len(batch) == 50
        batch.execute.assert_called_once()
        assert len(second_batch) == 5
        second_batch.execute.assert_called_once()

    def test_failed_execution(self, api, started_job, batch):
        """Should execute batch until there are no failed tasks"""
        jobs = [started_job for _ in range(49)]
        batch.execute.side_effect = [batch, batch, None]

        update_in_batch(api=api, jobs=jobs)

        assert started_job.update_job.call_count == 49
        assert len(api.new_batch.return_value) == 49
        assert batch.execute.call_count == 3


class TestInsightAsyncJob:
    """Test InsightAsyncJob class"""

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

    def test_update_job_expired(self, started_job, adreport, mocker):
        mocker.patch.object(started_job, "job_timeout", new=pendulum.Duration())

        started_job.update_job()
        assert started_job.failed

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
            edge_object=account,
            api=api,
            params={"breakdowns": [10, 20]},
            interval=interval,
        )

        assert str(job) == f"InsightAsyncJob(id=<None>, {account}, time_range=<Period [2010-01-01 -> 2011-01-01]>, breakdowns=[10, 20])"

    def test_get_result(self, job, adreport, api):
        job.start()
        api.call().json.return_value = {"data": [{"some_data": 123}, {"some_data": 77}]}

        result = job.get_result()

        adreport.get_result.assert_called_once()
        assert len(result) == 2
        assert isinstance(result[0], AdsInsights)
        assert result[0].export_all_data() == {"some_data": 123}
        assert result[1].export_all_data() == {"some_data": 77}

    def test_get_result_retried(self, mocker, job, api):
        job.start()
        api.call().json.return_value = {"data": [{"some_data": 123}, {"some_data": 77}]}
        ads_insights = AdsInsights(api=api)
        ads_insights._set_data({"items": [{"some_data": 123}, {"some_data": 77}]})
        with mocker.patch(
            "facebook_business.adobjects.objectparser.ObjectParser.parse_multiple",
            side_effect=[FacebookBadObjectError("Bad data to set object data"), ads_insights],
        ):
            # in case this is not retried, an error will be raised
            job.get_result()

    def test_get_result_when_job_is_not_started(self, job):
        with pytest.raises(RuntimeError, match=r"Incorrect usage of get_result - the job is not started or failed"):
            job.get_result()

    def test_get_result_when_job_is_failed(self, failed_job):
        with pytest.raises(RuntimeError, match=r"Incorrect usage of get_result - the job is not started or failed"):
            failed_job.get_result()

    @pytest.mark.parametrize(
        ("edge_class", "next_edge_class", "id_field"),
        [
            (AdAccount, Campaign, "campaign_id"),
            (Campaign, AdSet, "adset_id"),
            (AdSet, Ad, "ad_id"),
        ],
    )
    def test_split_job(self, mocker, api, edge_class, next_edge_class, id_field):
        """Test that split will correctly downsize edge_object"""
        today = pendulum.today().date()
        start, end = today - pendulum.duration(days=365 * 3 + 20), today - pendulum.duration(days=365 * 3 + 10)
        params = {"time_increment": 1, "breakdowns": []}
        job = InsightAsyncJob(api=api, edge_object=edge_class(1), interval=pendulum.Period(start, end), params=params)
        mocker.patch.object(edge_class, "get_insights", return_value=[{id_field: 1}, {id_field: 2}, {id_field: 3}])

        small_jobs = job.split_job()

        edge_class.get_insights.assert_called_once_with(
            params={
                "breakdowns": [],
                "fields": [id_field],
                "level": next_edge_class.__name__.lower(),
                "time_range": {
                    "since": (today - pendulum.duration(months=37) + pendulum.duration(days=1)).to_date_string(),
                    "until": end.to_date_string()
                },
            }
        )
        assert len(small_jobs) == 3
        assert all(j.interval == job.interval for j in small_jobs)
        for i, small_job in enumerate(small_jobs, start=1):
            assert small_job._params["time_range"] == job._params["time_range"]
            assert str(small_job) == f"InsightAsyncJob(id=<None>, {next_edge_class(i)}, time_range={job.interval}, breakdowns={[]})"

    def test_split_job_smallest(self, mocker, api):
        """Test that split will correctly downsize edge_object"""
        interval = pendulum.Period(pendulum.Date(2010, 1, 1), pendulum.Date(2010, 1, 10))
        params = {"time_increment": 1, "breakdowns": []}
        job = InsightAsyncJob(api=api, edge_object=Ad(1), interval=interval, params=params)

        with pytest.raises(ValueError, match="The job is already splitted to the smallest size."):
            job.split_job()


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

    def test_update_job(self, parent_job, grouped_jobs, api, batch):
        """Checks jobs status in advance and restart if some failed."""
        parent_job.update_job()

        # assert
        for job in grouped_jobs:
            job.update_job.assert_called_once_with(batch=batch)

    def test_get_result(self, parent_job, grouped_jobs):
        """Retrieve result of the finished job."""
        for job in grouped_jobs:
            job.get_result.return_value = []
        grouped_jobs[0].get_result.return_value = range(3, 8)
        grouped_jobs[6].get_result.return_value = range(4, 11)

        generator = parent_job.get_result()

        assert isinstance(generator, Iterator)
        assert list(generator) == list(range(3, 8)) + list(range(4, 11))

    def test_split_job(self, parent_job, grouped_jobs, mocker):
        grouped_jobs[0].failed = True
        grouped_jobs[0].split_job.return_value = [mocker.Mock(spec=InsightAsyncJob), mocker.Mock(spec=InsightAsyncJob)]
        grouped_jobs[5].failed = True
        grouped_jobs[5].split_job.return_value = [
            mocker.Mock(spec=InsightAsyncJob),
            mocker.Mock(spec=InsightAsyncJob),
            mocker.Mock(spec=InsightAsyncJob),
        ]

        small_jobs = parent_job.split_job()

        assert len(small_jobs) == len(grouped_jobs) + 5 - 2, "each failed job must be replaced with its split"
        for i, job in enumerate(grouped_jobs):
            if i in (0, 5):
                job.split_job.assert_called_once()
            else:
                job.split_job.assert_not_called()

    def test_split_job_smallest(self, parent_job, grouped_jobs):
        grouped_jobs[0].failed = True
        grouped_jobs[0].split_job.side_effect = ValueError("Mocking smallest size")

        # arbitrarily testing this X times, the max attempts is handled by async_job_manager rather than the job itself.
        count = 0
        while count < 10:
            split_jobs = parent_job.split_job()
            assert len(split_jobs) == len(
                grouped_jobs
            ), "attempted to split job at smallest size so should just restart job meaning same no. of jobs"
            grouped_jobs[0].attempt_number += 1
            count += 1

    def test_str(self, parent_job, grouped_jobs):
        assert str(parent_job) == f"ParentAsyncJob({grouped_jobs[0]} ... {len(grouped_jobs) - 1} jobs more)"
