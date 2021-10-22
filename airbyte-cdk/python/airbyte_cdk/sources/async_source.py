import collections
from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Union, Mapping

import pendulum
from airbyte_cdk.sources import AbstractSource
from pydantic.tools import Any


class JobWaitTimeout(Exception):
    pass


class AsyncJob(ABC):
    job_wait_timeout = None

    @property
    def job_sleep_intervals(self) -> Iterable[pendulum.duration]:
        """Sleep interval, also represents max number of retries"""
        return [pendulum.duration(seconds=secs) for secs in list(range(5)) * 2]

    @abstractmethod
    def start_job(self) -> None:
        """Create async job and return"""

    @abstractmethod
    def check_status(self) -> bool:
        """Something that will tell if job was successful"""

    def _wait_for_job(self):
        """Actual waiting for job to finish"""
        start_time = pendulum.now()
        for sleep_interval in self.job_sleep_intervals:
            finished_and_ok = self.check_status()
            if finished_and_ok:
                break
            # do we really need this?
            if self.job_wait_timeout and pendulum.now() - start_time > self.job_wait_timeout:
                raise JobWaitTimeout("Waiting for job more than allowed")
        else:
            # or this will be enough
            raise JobWaitTimeout("Waiting for job more than allowed")

    @abstractmethod
    def fetch_result(self) -> Any:
        """Reading job result, separate function because we want this to happen after we retrieved jobs in particular order"""


StreamSliceType = Union[Mapping[str, Any], AsyncJob, None]


class AsyncSource(AbstractSource, ABC):
    @abstractmethod
    @property
    def concurrent_limit(self):
        """Maximum number of concurrent jobs"""

    def iterate_over_slices(self, slices: Iterator[StreamSliceType]) -> Iterator[Mapping]:
        first_item = next(slices, None)
        if isinstance(first_item, AsyncJob):
            # FIXME: don't forget first item
            yield from self.iterate_over_jobs(jobs=slices)
        else:
            yield from slices

    def iterate_over_jobs(self, jobs: Iterator[AsyncJob]) -> Iterator[Mapping]:
        """ Produce slices in expected order

        :param jobs:
        [{
            "aaa": 1
            "something": instanceof(AsyncJob)
            "bb": 2
        },

        zip(sq1, sq2)

        (sq1[0], sq2[0]), (sq1[0], sq2[0])

        {non async} {async} {}
        {non async} {response}

        {non async} -> {non async}

        [{
            ...
            "aaa": 1,
            "something": result
            ...
        }]

        1. check slices if there any async jobs,
        2. start job, add it the queue
        q.appendleft()
        3. if queue is full wait and emit first item from the queue, restart any slice from the queue if needed (optional)
        get first item and wait for it,
        why we iterate over the rest? to restart or fail fast in case they fail
        if item[0]
        for item in q:
        q.pop()
        4. yield slice and continue with next slice at step #2

        [s, s, s, s] ... [s, s, s]

        мы запускаем  новую джобу только когда:
        - есть место, нужно это контролировать снаружи т.к. мы можем делать что-то полезное пока ждем место
        - джоба упала и ее можно перезапустить

        запустив джобу мы добавляем ее в очередь и если очередь полная то ждем самый старый элемент
        мы можем проверять статусы остальных джоб чтобы их перезапускать, но это не обязательно


        for slice in slices:
            q.appendleft(slice['job'])
            if q.full:
                slice['job'] = q.pop().get_result() # wait and retry
                yield slice

        while q.full:
            slice['job'] = q.pop().get_result() # wait and retry

        async
        threading
        subprocess
        cellery

        date
        account
        batch_id


        {
            "date": "",
            "

        }

        DateSlicesMixin -> slices = [now-30, now-29,.... now]

        AccountSubStream -> slices = [account_1, account_2]

        ReportStream(AccountSubStream, DateSlicesMixin):
        ReportStream -> slices = [(batch_1, account_1, now-30), (batch_1, account_1, now-30)]

        1. motivation - jobs+
        2. posibility -

        {
            slices()
        }


        {
            "job1": AsyncJob(....),
            "job2": AsyncJob(...),
            "date": 2131323,
        },
        {
            "job1": AsyncJob(....),
            "job2": AsyncJob(...),
            "date": 2131323,
        }

        {
            "job1": AsyncJob(...),
            "job1_result": <anything_that_fetch_result_returns>,
            "job2": AsyncJob(...),
            "job2_result": <anything_that_fetch_result_returns>,
        }


        slices = [AsyncJob(...), AsyncJob(...), AsyncJob(...)]

        start_async_job [                                 ] finished [fetch result]


        """
        running_jobs = collections.deque(maxlen=self.concurrent_limit)

        for job in jobs:
            job.start_job()
            running_jobs.appendleft(job)
            if len(running_jobs) == self.concurrent_limit:
                yield running_jobs.pop().get_result()

        while running_jobs:
            yield {
                running_jobs.pop().get_result()
            }
