#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import asyncio

import pendulum
from pendulum import duration
from typing import Any, Iterable, Mapping

from airbyte_cdk.sources.streams import Stream

import backoff

from abc import ABC, abstractmethod
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.common import retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


class JobWaitTimeout(Exception):
    """Job took too long to finish"""


class JobFailed(Exception):
    """Job finished with failed status"""


class AsyncStream(Stream, ABC):
    job_wait_timeout = None

    @abstractmethod
    @property
    def job_limit(self):
        """"""

    @property
    def job_sleep_intervals(self) -> Iterable[duration]:
        """Sleep interval, also represents max number of retries"""
        return [duration(seconds=secs) for secs in list(range(5)) * 2]

    def print(self, *args):
        print(self.name, *args)

    @abstractmethod
    async def create_job(
            self,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Any:
        """Create async job and return"""

    @backoff_policy
    async def create_and_wait(
            self,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ):
        """Single wait routing because we would like to re-create job in case its result is fail"""
        job = await self.create_job(stream_slice)
        await self.wait_for_job(job)

    @abstractmethod
    async def check_job_status(self, job) -> bool:
        """Something that will tell if job was successful"""

    @backoff_policy
    async def wait_for_job(self, job):
        """Actual waiting for job to finish"""
        self.print("waiting job", job)
        start_time = pendulum.now()
        for sleep_interval in self.job_sleep_intervals:
            finished_and_ok = await self.check_job_status(job)
            if finished_and_ok:
                break
            self.print(f"Sleeping {sleep_interval.total_seconds()} seconds while waiting for Job: {job} to complete")
            await asyncio.sleep(sleep_interval.total_seconds())
            # do we really need this?
            if self.job_wait_timeout and pendulum.now() - start_time > self.job_wait_timeout:
                raise JobWaitTimeout("Waiting for job more than allowed")
        else:
            # or this will be enough
            raise JobWaitTimeout("Waiting for job more than allowed")
        self.print("job finished")

    @abstractmethod
    async def fetch_job_result(self, job):
        """Reading job result, separate function because we want this to happen after we retrieved jobs in particular order"""

    @abstractmethod
    async def stream_slices(self, **kwargs):
        """Required to be async by aiostream lib in order to use stream.map"""
        yield None
