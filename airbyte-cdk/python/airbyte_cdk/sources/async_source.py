#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import collections
import itertools
from abc import ABC
from typing import Iterator, Union, Mapping, Optional


from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.source.async_job import AbstractAsyncJob
from pydantic.tools import Any


StreamSliceType = Union[Mapping[str, Any], AbstractAsyncJob, None]


class AbstractAsyncSource(AbstractSource, ABC):
    @property
    def concurrent_limit(self) -> Optional[int]:
        """Maximum number of concurrent jobs. By default it is None, meaning no limit"""
        return None

    def iterate_over_slices(self, slices: Iterator[StreamSliceType]) -> Iterator[Mapping]:
        """Wrapper to iterate over different kinds of slices.
        We generally support two kinds of slices:
        - sync - classic, dictionaries with values
        - async - instances of classes inherited from AbstractAsyncJob interface

        NOTE: this method may take a lot of time to execute in case of using with async slices.

        :param slices: slices iterable
        :yield: proper slice object, will wait async job for completion before yielding it
        """
        first_item = next(slices, None)
        all_slices = itertools.chain((first_item,), slices)
        if isinstance(first_item, AbstractAsyncJob):
            yield from self.iterate_over_jobs(jobs=all_slices)
        else:
            yield from all_slices

    def iterate_over_jobs(self, jobs: Iterator[AbstractAsyncJob]) -> Iterator[Mapping]:
        """ Produce slices in expected order

        :param jobs: async job

        input:
            {async job} {async job}

        output:
            {finished async job} {finished async job}

        Algorithm:
        1. check slices if there any async jobs,
        2. start job, add it the queue
        3. if queue is full wait and emit first item from the queue,
        4. (optional) restart any slice from the queue if needed
        5. get first item and wait for it,
        6. yield slice and continue with next slice at step #2

        """
        running_jobs = collections.deque(maxlen=self.concurrent_limit)

        for job in jobs:
            job.start_job()
            running_jobs.appendleft(job)
            if len(running_jobs) == self.concurrent_limit:
                current_job = running_jobs.pop()
                current_job.wait_completion()
                yield current_job

        while running_jobs:
            current_job = running_jobs.pop()
            current_job.wait_completion()
            yield current_job
