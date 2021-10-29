import collections
import itertools
import time
from abc import ABC, abstractmethod
from typing import Iterator, Union, Mapping

import pendulum
from airbyte_cdk.sources import AbstractSource
from pydantic.tools import Any


class JobWaitTimeout(Exception):
    pass


class AsyncJob(ABC):
    """Total time allowed for job to run, in case it is None the job will run endlessly"""
    job_wait_timeout = None

    @property
    @abstractmethod
    def job_sleep_interval(self) -> pendulum.Duration:
        """Sleep interval after each check of job status"""
        return pendulum.duration(seconds=5)

    @abstractmethod
    def start_job(self) -> None:
        """Create async job and return"""

    @abstractmethod
    def completed_successfully(self) -> bool:
        """Something that will tell if job was successful"""

    def should_retry(self, exc: Exception) -> bool:
        """Tell if the job should be restarted when the following exception caught"""
        return False

    def _wait_for_job(self):
        """Actual waiting for job to finish"""
        start_time = pendulum.now()

        while self.job_wait_timeout and pendulum.now() - start_time > self.job_wait_timeout:
            if self.completed_successfully():
                return
            time.sleep(self.job_sleep_interval.in_seconds())

        raise JobWaitTimeout("Waiting for job more than allowed")

    def fetch_result(self) -> Any:
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
        all_slices = itertools.chain((first_item,), slices)
        if isinstance(first_item, AsyncJob):
            yield from self.iterate_over_jobs(jobs=all_slices)
        else:
            yield from all_slices

    def iterate_over_jobs(self, jobs: Iterator[AsyncJob]) -> Iterator[Mapping]:
        """ Produce slices in expected order

        :param jobs:

        input:
            {non async} {async} {}

        output:
            {non async} {response} {}

        1. check slices if there any async jobs,
        2. start job, add it the queue
        q.appendleft()
        3. if queue is full wait and emit first item from the queue, restart any slice from the queue if needed (optional)
        get first item and wait for it,
        why we iterate over the rest? to restart or fail fast in case they fail
        4. yield slice and continue with next slice at step #2

        """
        running_jobs = collections.deque(maxlen=self.concurrent_limit)

        for job in jobs:
            job.start_job()
            running_jobs.appendleft(job)
            if len(running_jobs) == self.concurrent_limit:
                yield running_jobs.pop().fetch_result()

        while running_jobs:
            yield {
                running_jobs.pop().fetch_result()
            }
