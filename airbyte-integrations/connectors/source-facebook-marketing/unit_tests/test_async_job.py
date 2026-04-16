#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import time
from datetime import date, datetime, timedelta

import freezegun
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
from source_facebook_marketing.utils import DateInterval

from airbyte_cdk.utils.datetime_helpers import ab_datetime_now
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class DummyAPILimit:
    """
    Test double for APILimit:
      - Never throttles
      - Keeps basic inflight accounting
      - No external API calls
    """

    def __init__(self):
        self._inflight = 0
        self._current_throttle = 0.0
        self.max_jobs = 10**9
        self.throttle_limit = 10**9

    # ---- scheduling ----
    def try_consume(self) -> bool:
        self._inflight += 1
        return True

    def release(self) -> None:
        if self._inflight > 0:
            self._inflight -= 1

    @property
    def limit_reached(self) -> bool:
        return False

    # ---- optional introspection ----
    @property
    def inflight(self) -> int:
        return self._inflight

    @property
    def current_throttle(self) -> float:
        return self._current_throttle


class DummyRun:
    """
    Minimal AdReportRun stand-in:
      - first api_get() call: RUNNING
      - second api_get() call: COMPLETED
      - get_result(): returns fake rows with the requested id field
    """

    def __init__(self, id_field: str):
        self._id_field = id_field
        self._calls = 0
        self._status = Status.RUNNING
        self._percent = 0

    def api_get(self):
        self._calls += 1
        if self._calls >= 2:
            self._status = Status.COMPLETED
            self._percent = 100
        else:
            self._status = Status.RUNNING
            self._percent = 50
        return self

    def get(self, key):
        if key == "async_status":
            return self._status
        if key == "async_percent_completion":
            return self._percent
        raise KeyError(key)

    # FB SDK typically supports dict-style indexing too
    def __getitem__(self, key):
        return self.get(key)

    def get_result(self, params=None):
        # three rows with the requested PK field
        return [{self._id_field: 1}, {self._id_field: 2}, {self._id_field: 3}]


@pytest.fixture(name="api_limit")
def api_limit_fixture():
    return DummyAPILimit()


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
        "breakdowns": [],
        "fields": ["field1", "field2"],
        "time_increment": 1,
        "action_attribution_windows": [],
    }
    interval = DateInterval(date(2019, 1, 1), date(2019, 1, 1))

    return InsightAsyncJob(
        edge_object=account,
        api=api,
        interval=interval,
        params=params,
        job_timeout=timedelta(minutes=60),
    )


@pytest.fixture(name="grouped_jobs")
def grouped_jobs_fixture(mocker):
    return [
        mocker.Mock(spec=InsightAsyncJob, attempt_number=1, failed=False, completed=False, started=False, elapsed_time=None, new_jobs=[])
        for _ in range(10)
    ]


@pytest.fixture(name="parent_job")
def parent_job_fixture(api, grouped_jobs):
    interval = DateInterval(date(2019, 1, 1), date(2019, 1, 1))
    return ParentAsyncJob(api=api, jobs=grouped_jobs, interval=interval)


@pytest.fixture(name="started_job")
def started_job_fixture(job, adreport, mocker, api_limit):
    adreport["async_status"] = Status.RUNNING.value
    adreport["async_percent_completion"] = 0
    mocker.patch.object(job, "update_job", wraps=job.update_job)
    job.start(api_limit)

    return job


@pytest.fixture(name="completed_job")
def completed_job_fixture(started_job, adreport):
    adreport["async_status"] = Status.COMPLETED.value
    adreport["async_percent_completion"] = 100
    started_job.update_job()
    started_job._check_status()

    return started_job


@pytest.fixture(name="late_job")
def late_job_fixture(started_job, adreport):
    adreport["async_status"] = Status.COMPLETED.value
    adreport["async_percent_completion"] = 100
    started_job.update_job()

    return started_job


@pytest.fixture(name="failed_job")
def failed_job_fixture(started_job, adreport, api_limit, mocker):
    adreport["async_status"] = Status.FAILED.value
    adreport["async_percent_completion"] = 0
    started_job._check_status()
    started_job.start(api_limit)
    mocker.patch.object(started_job, "_split_by_edge_class")
    started_job._check_status()

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

    def test_start(self, job, api_limit):
        job.start(api_limit)

        assert job._job
        assert job.elapsed_time

    def test_start_already_started(self, job, api_limit):
        job.start(api_limit)

        with pytest.raises(
            RuntimeError,
            match=r": Incorrect usage of start - the job already started, use restart instead",
        ):
            job.start(api_limit)

    def test_update_job_not_started(self, job):
        # update_in_batch just skips the not started jobs
        job.update_job()

    def test_update_job_on_completed_job(self, completed_job, adreport):
        completed_job.update_job()

        adreport.api_get.assert_called_once()

    def test_update_job(self, started_job, adreport):
        started_job.update_job()

        adreport.api_get.assert_called_once()

    def test_update_job_expired(self, started_job, adreport, mocker):
        mocker.patch.object(started_job, "_job_timeout", new=timedelta())

        started_job._check_status()
        # Ready for restart
        assert started_job.started == False
        assert started_job.completed == False
        assert started_job.failed == False

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

    def test_elapsed_time(self, job, api, adreport, api_limit):
        assert job.elapsed_time is None, "should be None for the job that is not started"

        job.start(api_limit)
        adreport["async_status"] = Status.COMPLETED.value
        adreport["async_percent_completion"] = 0
        job._check_status()

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
        assert not failed_job.completed
        assert failed_job.failed

    def test_completed_skipped(self, failed_job, api, adreport):
        adreport["async_status"] = Status.SKIPPED.value
        assert not failed_job.completed
        assert failed_job.failed

    def test_failed_no(self, job):
        assert not job.failed, "should return False for active job"

    def test_failed_yes(self, failed_job):
        assert failed_job.failed, "should return True if the job previously failed"

    def test_str(self, api, account):
        interval = DateInterval(date(2010, 1, 1), date(2011, 1, 1))
        job = InsightAsyncJob(
            edge_object=account,
            api=api,
            params={"breakdowns": [10, 20]},
            interval=interval,
            job_timeout=timedelta(minutes=60),
        )

        assert (
            str(job)
            == f"InsightAsyncJob(id=<None>, {account}, time_range=DateInterval(2010-01-01 to 2011-01-01), breakdowns=[10, 20], fields=[])"
        )

    def test_get_result(self, job, adreport, api, api_limit):
        job.start(api_limit)
        api.call().json.return_value = {"data": [{"some_data": 123}, {"some_data": 77}]}

        result = job.get_result()

        adreport.get_result.assert_called_once()
        assert len(result) == 2
        assert isinstance(result[0], AdsInsights)
        assert result[0].export_all_data() == {"some_data": 123}
        assert result[1].export_all_data() == {"some_data": 77}

    def test_get_result_retried(self, mocker, job, api, api_limit):
        job.start(api_limit)
        api.call().json.return_value = {"data": [{"some_data": 123}, {"some_data": 77}]}
        ads_insights = AdsInsights(api=api)
        ads_insights._set_data({"items": [{"some_data": 123}, {"some_data": 77}]})
        mocker.patch(
            "facebook_business.adobjects.objectparser.ObjectParser.parse_multiple",
            side_effect=[
                FacebookBadObjectError("Bad data to set object data"),
                ads_insights,
            ],
        )

        # in case this is not retried, an error will be raised
        job.get_result()

    def test_get_result_when_job_is_not_started(self, job):
        with pytest.raises(
            RuntimeError,
            match=r"Incorrect usage of get_result - the job is not started or failed",
        ):
            job.get_result()

    def test_get_result_when_job_is_failed(self, failed_job):
        with pytest.raises(
            RuntimeError,
            match=r"Incorrect usage of get_result - the job is not started or failed",
        ):
            failed_job.get_result()

    @pytest.mark.parametrize(
        ("edge_class", "next_edge_class", "id_field"),
        [
            (AdAccount, Campaign, "campaign_id"),
            (Campaign, AdSet, "adset_id"),
            (AdSet, Ad, "ad_id"),
        ],
    )
    @freezegun.freeze_time("2023-10-29")
    def test_split_job_params_and_children(self, mocker, api, edge_class, next_edge_class, id_field):
        """Verify we call edge.get_insights with correct params and produce children with that edge."""
        today = ab_datetime_now().date()
        start = today - timedelta(days=365 * 3 + 20)
        end = today - timedelta(days=365 * 3 + 10)

        params = {"time_increment": 1, "breakdowns": []}
        job = InsightAsyncJob(
            api=api,
            edge_object=edge_class(1),
            interval=DateInterval(start, end),
            params=params,
            job_timeout=timedelta(minutes=60),
        )

        # Patch the *instance* method so we can assert exact kwargs and return our DummyRun
        def fake_get_insights(params, is_async):
            assert is_async is True
            return DummyRun(id_field)

        inst_mock = mocker.patch.object(job._edge_object, "get_insights", side_effect=fake_get_insights)

        # Execute the split
        small_jobs = job._split_by_edge_class(next_edge_class)

        # ----- Assert the params passed to get_insights --------------------------
        expected_since = (job._interval.start - timedelta(days=29)).strftime("%Y-%m-%d")

        expected_params = {
            "fields": [id_field],
            "level": next_edge_class.__name__.lower(),
            "time_range": {
                "since": expected_since,
                "until": job._interval.end.strftime("%Y-%m-%d"),
            },
        }

        inst_mock.assert_called_once()
        called_kwargs = inst_mock.call_args.kwargs
        assert called_kwargs["params"] == expected_params
        assert called_kwargs["is_async"] is True

        # ----- Assert children created correctly --------------------------------
        assert len(small_jobs) == 3
        assert all(isinstance(j._edge_object, next_edge_class) for j in small_jobs)
        assert all(j.interval == job.interval for j in small_jobs)
        for child in small_jobs:
            assert child._params["time_range"] == job._params["time_range"]

    @pytest.mark.parametrize(
        "fields",
        [
            ["ad_id", "clicks", "impressions", "spend"],  # 3 non-PK -> mid=1
            ["ad_id", "f1", "f2"],  # 2 non-PK -> mid=1
            ["ad_id", "c1", "c2", "c3", "c4"],  # 4 non-PK -> mid=2
        ],
    )
    def test_split_job_by_fields_parent_creates_children(self, mocker, api, fields):
        """
        When the edge is Ad, _split_job() should return a list with a single ParentAsyncJob
        that contains two child InsightAsyncJobs whose fields are split (PK + half/half).
        """
        from source_facebook_marketing.streams.async_job import InsightAsyncJob, ParentAsyncJob

        interval = DateInterval(date(2010, 1, 1), date(2010, 1, 10))
        params = {"time_increment": 1, "breakdowns": [], "fields": fields}
        pk = ["ad_id"]

        job = InsightAsyncJob(
            api=api,
            edge_object=Ad(1),
            interval=interval,
            params=params,
            job_timeout=timedelta(minutes=60),
            primary_key=pk,
        )

        result = job._split_job()
        assert isinstance(result, list) and len(result) == 1
        parent = result[0]
        assert isinstance(parent, ParentAsyncJob)

        # exactly two children
        children = parent._jobs
        assert len(children) == 2
        for child in children:
            assert isinstance(child, InsightAsyncJob)
            assert isinstance(child._edge_object, Ad)
            assert child.interval == interval

        # expected split
        non_pk = [f for f in fields if f not in pk]
        mid = len(non_pk) // 2
        expected_a = pk + non_pk[:mid]
        expected_b = pk + non_pk[mid:]

        fields_a = children[0]._params["fields"]
        fields_b = children[1]._params["fields"]
        assert fields_a == expected_a
        assert fields_b == expected_b

    @pytest.mark.parametrize(
        "fields",
        [
            ["ad_id"],  # 0 non-PK
            ["ad_id", "only_one"],  # 1 non-PK
        ],
    )
    def test_split_job_by_fields_parent_not_enough_fields(self, api, fields):
        """
        If there are <=1 non-PK fields, splitting by fields is impossible and should raise.
        """
        from source_facebook_marketing.streams.async_job import InsightAsyncJob

        interval = DateInterval(date(2010, 1, 1), date(2010, 1, 10))
        params = {"time_increment": 1, "breakdowns": [], "fields": fields}
        pk = ["ad_id"]

        job = InsightAsyncJob(
            api=api,
            edge_object=Ad(1),
            interval=interval,
            params=params,
            job_timeout=timedelta(minutes=60),
            primary_key=pk,
        )

        with pytest.raises(AirbyteTracedException, match="Cannot split by fields") as exc_info:
            job._split_job()

        from airbyte_cdk.models import FailureType

        assert exc_info.value.failure_type == FailureType.system_error

    @freezegun.freeze_time("2023-10-29")
    def test_collect_child_ids_start_failure_generic(self, mocker, api):
        """
        When get_insights raises a non-FacebookRequestError exception,
        _collect_child_ids should wrap it in AirbyteTracedException with transient_error.
        """
        from airbyte_cdk.models import FailureType

        job = InsightAsyncJob(
            api=api,
            edge_object=AdAccount(1),
            interval=DateInterval(date(2023, 1, 1), date(2023, 1, 10)),
            params={"time_increment": 1, "breakdowns": []},
            job_timeout=timedelta(minutes=60),
        )
        mocker.patch.object(job._edge_object, "get_insights", side_effect=RuntimeError("API down"))

        with pytest.raises(AirbyteTracedException, match="Failed to start ID-collection job") as exc_info:
            job._collect_child_ids(pk_name="campaign_id", level="campaign")

        assert exc_info.value.failure_type == FailureType.transient_error

    @freezegun.freeze_time("2023-10-29")
    def test_collect_child_ids_start_failure_facebook_request_error(self, mocker, api):
        """
        When get_insights raises a FacebookRequestError, _collect_child_ids should
        delegate to traced_exception() to preserve the correct FailureType classification
        (e.g. config_error for invalid tokens, transient_error for rate limits).
        """
        from unittest.mock import PropertyMock

        from facebook_business.exceptions import FacebookRequestError

        from airbyte_cdk.models import FailureType

        job = InsightAsyncJob(
            api=api,
            edge_object=AdAccount(1),
            interval=DateInterval(date(2023, 1, 1), date(2023, 1, 10)),
            params={"time_increment": 1, "breakdowns": []},
            job_timeout=timedelta(minutes=60),
        )

        # Simulate a FacebookRequestError with an invalid-token message
        fb_error = FacebookRequestError(
            message="Invalid OAuth access token",
            request_context={"method": "GET"},
            http_status=400,
            http_headers={},
            body='{"error": {"message": "Invalid OAuth access token", "type": "OAuthException", "code": 190, "fbtrace_id": "abc"}}',
        )
        mocker.patch.object(job._edge_object, "get_insights", side_effect=fb_error)

        with pytest.raises(AirbyteTracedException) as exc_info:
            job._collect_child_ids(pk_name="campaign_id", level="campaign")

        # traced_exception classifies invalid token errors as config_error
        assert exc_info.value.failure_type == FailureType.config_error

    @freezegun.freeze_time("2023-10-29")
    def test_collect_child_ids_all_attempts_exhausted(self, mocker, api):
        """
        When every attempt returns Job Failed, _collect_child_ids should raise
        AirbyteTracedException with transient_error after exhausting all retries.
        """
        from airbyte_cdk.models import FailureType

        job = InsightAsyncJob(
            api=api,
            edge_object=AdAccount(1),
            interval=DateInterval(date(2023, 1, 1), date(2023, 1, 10)),
            params={"time_increment": 1, "breakdowns": []},
            job_timeout=timedelta(minutes=60),
        )

        # Create a mock that always returns Job Failed status
        failed_run = mocker.MagicMock()
        failed_run.api_get.return_value = failed_run
        failed_run.get.side_effect = lambda key: {
            "async_status": Status.FAILED,
            "async_percent_completion": 0,
        }[key]

        mocker.patch.object(job._edge_object, "get_insights", return_value=failed_run)
        mocker.patch("source_facebook_marketing.streams.async_job.time.sleep")

        with pytest.raises(AirbyteTracedException, match="ID-collection failed for level=campaign") as exc_info:
            job._collect_child_ids(pk_name="campaign_id", level="campaign")

        assert exc_info.value.failure_type == FailureType.transient_error

    @freezegun.freeze_time("2023-10-29")
    def test_collect_child_ids_result_fetch_failure(self, mocker, api):
        """
        When get_result raises FacebookBadObjectError, _collect_child_ids should
        wrap it in AirbyteTracedException with transient_error.
        """
        from airbyte_cdk.models import FailureType

        job = InsightAsyncJob(
            api=api,
            edge_object=AdAccount(1),
            interval=DateInterval(date(2023, 1, 1), date(2023, 1, 10)),
            params={"time_increment": 1, "breakdowns": []},
            job_timeout=timedelta(minutes=60),
        )

        # Create a mock that completes immediately but fails on get_result
        completed_run = mocker.MagicMock()
        completed_run.api_get.return_value = completed_run
        completed_run.get.side_effect = lambda key: {
            "async_status": Status.COMPLETED,
            "async_percent_completion": 100,
        }[key]
        completed_run.get_result.side_effect = FacebookBadObjectError("bad object")

        mocker.patch.object(job._edge_object, "get_insights", return_value=completed_run)

        with pytest.raises(AirbyteTracedException, match="Failed to fetch ID-collection results") as exc_info:
            job._collect_child_ids(pk_name="campaign_id", level="campaign")

        assert exc_info.value.failure_type == FailureType.transient_error

    @freezegun.freeze_time("2023-10-29")
    def test_collect_child_ids_no_child_ids(self, mocker, api):
        """
        When _collect_child_ids returns an empty list, _split_by_edge_class should
        raise AirbyteTracedException with system_error.
        """
        from airbyte_cdk.models import FailureType

        job = InsightAsyncJob(
            api=api,
            edge_object=AdAccount(1),
            interval=DateInterval(date(2023, 1, 1), date(2023, 1, 10)),
            params={"time_increment": 1, "breakdowns": []},
            job_timeout=timedelta(minutes=60),
        )

        # Create a mock that completes immediately and returns no IDs
        completed_run = mocker.MagicMock()
        completed_run.api_get.return_value = completed_run
        completed_run.get.side_effect = lambda key: {
            "async_status": Status.COMPLETED,
            "async_percent_completion": 100,
        }[key]
        completed_run.get_result.return_value = []  # no rows → no IDs

        mocker.patch.object(job._edge_object, "get_insights", return_value=completed_run)

        with pytest.raises(AirbyteTracedException, match="No child IDs at level=campaign") as exc_info:
            job._split_by_edge_class(Campaign)

        assert exc_info.value.failure_type == FailureType.system_error

    @freezegun.freeze_time("2023-10-29")
    def test_collect_child_ids_timeout(self, mocker, api):
        """
        When job polling exceeds the timeout, _collect_child_ids should raise
        AirbyteTracedException with transient_error.
        """
        from airbyte_cdk.models import FailureType

        job = InsightAsyncJob(
            api=api,
            edge_object=AdAccount(1),
            interval=DateInterval(date(2023, 1, 1), date(2023, 1, 10)),
            params={"time_increment": 1, "breakdowns": []},
            job_timeout=timedelta(seconds=1),
        )

        # Create a mock that is always running (never completes)
        running_run = mocker.MagicMock()
        running_run.api_get.return_value = running_run
        running_run.get.side_effect = lambda key: {
            "async_status": Status.RUNNING,
            "async_percent_completion": 50,
        }[key]

        mocker.patch.object(job._edge_object, "get_insights", return_value=running_run)
        # Patch sleep to be a no-op, and advance time past the timeout
        mocker.patch("source_facebook_marketing.streams.async_job.time.sleep")

        # Patch ab_datetime_now to advance past timeout on the second call
        original_now = ab_datetime_now()
        call_count = [0]

        def advancing_now():
            call_count[0] += 1
            if call_count[0] <= 1:
                return original_now
            # Return a time well past the 1-second timeout
            return original_now + timedelta(seconds=10)

        mocker.patch("source_facebook_marketing.streams.async_job.ab_datetime_now", side_effect=advancing_now)

        with pytest.raises(AirbyteTracedException, match="ID-collection timed out") as exc_info:
            job._collect_child_ids(pk_name="campaign_id", level="campaign")

        assert exc_info.value.failure_type == FailureType.transient_error


class TestParentAsyncJob:
    def test_start(self, parent_job, grouped_jobs, api_limit):
        # should attempt to start every child (DummyAPILimit never limits)
        parent_job.start(api_limit)
        for job in grouped_jobs:
            job.start.assert_called_once_with(api_limit)

    def test_completed(self, parent_job, grouped_jobs):
        assert not parent_job.completed, "initially not completed"

        # partially complete
        grouped_jobs[0].completed = True
        grouped_jobs[5].completed = True
        assert not parent_job.completed, "not completed until all jobs completed"

        # complete all
        for j in grouped_jobs:
            j.completed = True
        assert parent_job.completed, "completed because all jobs completed"

    def test_update_job_forwards_batch(self, parent_job, grouped_jobs, batch, api_limit):
        for job in grouped_jobs:
            job.started = True
        parent_job.update_job(batch=batch)
        for j in grouped_jobs:
            j.update_job.assert_called_once_with(batch=batch)

    def test_update_job_splices_new_children(self, mocker, api, batch):
        """
        If a child sets .new_jobs = [ParentAsyncJob(...)] then parent.update_job()
        should replace that child with the inner children from the provided ParentAsyncJob.
        """
        interval = DateInterval(date(2020, 1, 1), date(2020, 1, 2))

        # Two original children
        child0 = mocker.Mock(spec=InsightAsyncJob, started=True, completed=False, new_jobs=[])
        child1 = mocker.Mock(spec=InsightAsyncJob, started=True, completed=False, new_jobs=[])
        # Their update_job should accept batch
        child0.update_job = mocker.Mock()
        child1.update_job = mocker.Mock()

        # New children that will replace child0
        new_a = mocker.Mock(spec=InsightAsyncJob, started=False, completed=False, new_jobs=[])
        new_b = mocker.Mock(spec=InsightAsyncJob, started=False, completed=False, new_jobs=[])

        # child0 announces work split: one ParentAsyncJob with two kids
        child0.new_jobs = [
            ParentAsyncJob(api=api, jobs=[new_a, new_b], interval=interval)  # minimal required args
        ]

        parent = ParentAsyncJob(api=api, jobs=[child0, child1], interval=interval)

        # run update to forward polling and splice children
        parent.update_job(batch=batch)

        # update forwarded to both original children
        child0.update_job.assert_called_once_with(batch=batch)
        child1.update_job.assert_called_once_with(batch=batch)

        # child0 replaced by (new_a, new_b), child1 preserved → total 3
        assert parent._jobs == [new_a, new_b, child1]

    def test_get_result_streams_children(self, parent_job, grouped_jobs):
        """
        With no primary key provided, get_result() yields results from children in order.
        """
        for j in grouped_jobs:
            j.get_result.return_value = []
        grouped_jobs[0].get_result.return_value = range(3, 8)
        grouped_jobs[6].get_result.return_value = range(4, 11)

        out = list(parent_job.get_result())
        assert out == list(range(3, 8)) + list(range(4, 11))

    def test_get_result_merges_by_primary_key(self, mocker, api):
        """
        With primary_key set, rows from children with the same PK should merge,
        and later children overwrite non-PK fields.
        """
        interval = DateInterval(date(2020, 1, 1), date(2020, 1, 1))
        pk = ["id"]

        c1 = mocker.Mock(spec=InsightAsyncJob)
        c2 = mocker.Mock(spec=InsightAsyncJob)

        # child1 provides base rows
        c1.get_result.return_value = [
            {"id": 1, "a": 1},
            {"id": 2, "a": 2},
        ]
        # child2 overwrites/extends id=1
        c2.get_result.return_value = [
            {"id": 1, "b": 10},
            {"id": 1, "a": 100},
        ]

        parent = ParentAsyncJob(api=api, jobs=[c1, c2], interval=interval, primary_key=pk)

        rows = list(parent.get_result())
        # Convert ParentAsyncJob._ExportableRow to dicts
        as_dicts = [r.export_all_data() if hasattr(r, "export_all_data") else dict(r) for r in rows]

        # Expect merged records for ids {1,2}; for id=1, 'a' overwritten to 100, 'b' added
        # Ordering by insertion of dict values isn't guaranteed; normalize by PK
        merged = {d["id"]: d for d in as_dicts}
        assert set(merged.keys()) == {1, 2}
        assert merged[1]["a"] == 100
        assert merged[1]["b"] == 10
        assert merged[2]["a"] == 2

    def test_get_result_merges_with_object_breakdown_id_injection(self, mocker, api):
        """
        When object_breakdowns is provided (e.g. {'image_asset': 'image_asset_id'}),
        the parent should inject the *_id from nested objects before computing the PK
        and merge accordingly.
        """
        interval = DateInterval(date(2020, 1, 1), date(2020, 1, 1))
        pk = ["image_asset_id"]
        ob_map = {"image_asset": "image_asset_id"}

        c1 = mocker.Mock(spec=InsightAsyncJob)
        c2 = mocker.Mock(spec=InsightAsyncJob)

        # c1: no explicit *_id, but has the object with an "id"
        c1.get_result.return_value = [{"image_asset": {"id": "img-123"}, "metric": 1}]
        # c2: explicit *_id for same asset, adds more fields
        c2.get_result.return_value = [{"image_asset_id": "img-123", "metric2": 2}]

        parent = ParentAsyncJob(
            api=api,
            jobs=[c1, c2],
            interval=interval,
            primary_key=pk,
            object_breakdowns=ob_map,
        )

        rows = list(parent.get_result())
        as_dicts = [r.export_all_data() if hasattr(r, "export_all_data") else dict(r) for r in rows]

        assert len(as_dicts) == 1
        merged = as_dicts[0]
        # injected ID should exist
        assert merged["image_asset_id"] == "img-123"
        # both metrics present
        assert merged["metric"] == 1
        assert merged["metric2"] == 2

    def test_str(self, parent_job, grouped_jobs):
        assert str(parent_job) == f"ParentAsyncJob({grouped_jobs[0]} ... {len(grouped_jobs) - 1} jobs more)"


class TestAPILimitTypeAnnotation:
    """Verify that the APILimit forward reference in async_job.py resolves correctly.

    async_job_manager imports from async_job, so a runtime import would be
    circular.  The fix adds a TYPE_CHECKING-guarded import so that static
    analysis tools (mypy, pyflakes) can resolve the ``"APILimit"`` string
    annotation.  At runtime we supply the namespace explicitly to
    ``typing.get_type_hints`` — the same thing type-checkers do internally.
    """

    @pytest.mark.parametrize(
        "cls_name",
        [
            pytest.param("AsyncJob", id="abstract_base"),
            pytest.param("InsightAsyncJob", id="leaf_job"),
            pytest.param("ParentAsyncJob", id="parent_job"),
        ],
    )
    def test_start_method_apilimit_annotation_resolves(self, cls_name):
        """The 'APILimit' string annotation on <cls>.start() must resolve
        to the real class when the proper namespace is provided."""
        import importlib
        import typing

        from source_facebook_marketing.streams.async_job_manager import APILimit

        mod = importlib.import_module("source_facebook_marketing.streams.async_job")
        cls = getattr(mod, cls_name)
        # Provide the module globals + APILimit so get_type_hints can resolve the forward ref,
        # mirroring what static type-checkers do with the TYPE_CHECKING import.
        ns = {**vars(mod), "APILimit": APILimit}
        hints = typing.get_type_hints(cls.start, globalns=ns)
        assert hints["api_limit"] is APILimit
