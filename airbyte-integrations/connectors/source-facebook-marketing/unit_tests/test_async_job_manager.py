#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import math
from unittest.mock import MagicMock, PropertyMock, patch

import pendulum
import pytest
from source_facebook_marketing.streams.async_job_manager import InsightsAsyncJobManager


@pytest.fixture(autouse=False)
def logger_mock():
    with patch(
        "source_facebook_marketing.streams.async_job_manager.logger",
    ) as log_mock:
        yield log_mock


@pytest.fixture(scope="function")
def job_mock():
    with patch("source_facebook_marketing.streams.async_job_manager.AsyncJob", PropertyMock()) as async_job_mock:
        async_job_mock.return_value = async_job_mock
        async_job_mock.failed = False
        yield async_job_mock


def make_api_mock():
    api_mock = MagicMock()
    api_mock.api.ads_insights_throttle = 0.5, 0.5
    api_mock.api.new_batch.return_value = api_mock
    api_mock.execute.return_value = None
    return api_mock


@pytest.mark.parametrize(
    "from_date,to_date",
    [
        ("2020-10-10", "2021-10-10"),
        ("2021-10-09", "2021-10-10"),
    ],
)
def test_async_job_manager(job_mock, from_date, to_date):
    from_date, to_date = pendulum.parse(from_date), pendulum.parse(to_date)
    assert from_date <= to_date
    api_mock = make_api_mock()
    job_manager = InsightsAsyncJobManager(
        api=api_mock,
        job_params={"breakdowns": []},
        from_date=from_date,
        to_date=to_date,
    )
    job_manager.add_async_jobs()
    assert not job_manager.done()
    jobs = []
    while not job_manager.done():
        jobs.append(job_manager.get_next_completed_job())
    assert len(jobs) == max((to_date - from_date).total_days(), 1)
    assert job_manager.done()


@pytest.mark.skip("Now this case is failing, fix it later")
def test_async_job_manager_to_date_greater_from(job_mock):
    from_date, to_date = pendulum.parse("2020-10-10"), pendulum.parse("2019-10-10")
    assert from_date > to_date
    api_mock = make_api_mock()
    job_manager = InsightsAsyncJobManager(
        api=api_mock,
        job_params={"breakdowns": []},
        from_date=from_date,
        to_date=to_date,
    )
    job_manager.add_async_jobs()
    assert job_manager.done()


def test_job_failed(job_mock):
    from_date, to_date = pendulum.parse("2019-10-10"), pendulum.parse("2019-10-10")
    api_mock = make_api_mock()
    job_manager = InsightsAsyncJobManager(
        api=api_mock,
        job_params={"breakdowns": []},
        from_date=from_date,
        to_date=to_date,
    )
    job_mock.failed = True
    job_manager.add_async_jobs()
    assert not job_manager.done()
    with pytest.raises(Exception, match=r"^Job .* failed$"):
        job_manager.get_next_completed_job()
    assert job_mock.restart.called


def test_job_failed_two_times(job_mock):
    from_date, to_date = pendulum.parse("2019-10-10"), pendulum.parse("2019-10-10")
    api_mock = make_api_mock()
    job_manager = InsightsAsyncJobManager(
        api=api_mock,
        job_params={"breakdowns": []},
        from_date=from_date,
        to_date=to_date,
    )
    job_manager.add_async_jobs()
    assert not job_manager.done()
    type(job_mock).failed = PropertyMock(side_effect=[True, True, False])
    while not job_manager.done():
        job_manager.get_next_completed_job()
    assert job_mock.restart.called
    assert job_mock.restart.call_count == 2


def test_job_wait_unitll_completed(job_mock, time_sleep_mock):
    from_date, to_date = pendulum.parse("2019-10-10"), pendulum.parse("2019-10-10")
    api_mock = make_api_mock()
    job_manager = InsightsAsyncJobManager(
        api=api_mock,
        job_params={"breakdowns": []},
        from_date=from_date,
        to_date=to_date,
    )
    job_manager.add_async_jobs()
    assert not job_manager.done()
    type(job_mock).completed = PropertyMock(side_effect=[False, False, True])
    while not job_manager.done():
        job_manager.get_next_completed_job()
    assert not job_mock.restart.called
    time_sleep_mock.assert_called_with(30)
