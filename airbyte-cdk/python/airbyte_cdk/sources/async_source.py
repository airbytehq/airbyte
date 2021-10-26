import collections
from abc import ABC, abstractmethod
from typing import Iterator, Union, Mapping

import pendulum
from airbyte_cdk.sources import AbstractSource
from pydantic.tools import Any


class JobWaitTimeout(Exception):
    pass


class AsyncJob(ABC):
    job_wait_timeout = None

    @property
    @abstractmethod
    def job_sleep_interval(self):
        return pendulum.duration(seconds=5)

    @abstractmethod
    def start_job(self) -> None:
        """Create async job and return"""

    @abstractmethod
    def check_status(self) -> bool:
        """Something that will tell if job was successful"""

    def _wait_for_job(self):
        """Actual waiting for job to finish"""
        start_time = pendulum.now()

        while self.job_wait_timeout and pendulum.now() - start_time > self.job_wait_timeout:
            finished_and_ok = self.check_status()
            if finished_and_ok:
                return

        raise JobWaitTimeout("Waiting for job more than allowed")

    def get_result(self) -> Any:
        """Reading job result, separate function because we want this to happen after we retrieved jobs in particular order"""
        self._wait_for_job()
        return self


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

        for slice in slices:
            q.appendleft(slice['job'])
            if q.full:
                slice['job'] = q.pop().get_result() # wait and retry
                yield slice

        while q.full:
            slice['job'] = q.pop().get_result() # wait and retry

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
