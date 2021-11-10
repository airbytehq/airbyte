import time
from abc import ABC, abstractmethod
from typing import Optional

import pendulum


class JobWaitTimeout(Exception):
    pass


class AbstractAsyncJob(ABC):
    """ Abstract base class for AsyncJobs.
    The user of this will need to implement at least start_job and completed_successfully methods
    """
    @property
    def job_wait_timeout(self) -> Optional[pendulum.Duration]:
        """Total time allowed for job to run, in case it is None the job may run endlessly"""
        return None

    @property
    def job_sleep_interval(self) -> pendulum.Duration:
        """Sleep interval between each call of completed_successfully"""
        return pendulum.duration(seconds=5)

    @abstractmethod
    def start_job(self) -> None:
        """Create async job and return. Here should all calls required for the job to start.
        After this point only calls to completed_successfully will be happening.
        """

    @abstractmethod
    def completed_successfully(self) -> bool:
        """Something that will tell if job was successful.
        This method should check job status and return True only if it is successfull.
        It is expected the this method will raise exception in case of job failure.
        """

    def should_retry(self, exc: Exception) -> bool:
        """Tells if the job should be restarted when the following exception occurs.
        TODO: implement restart logic"""
        return False

    def wait_completion(self):
        """Actual waiting for job to finish"""
        start_time = pendulum.now()

        while self.job_wait_timeout and pendulum.now() - start_time > self.job_wait_timeout:
            if self.completed_successfully():
                return
            time.sleep(self.job_sleep_interval.in_seconds())

        raise JobWaitTimeout("Waiting for job more than allowed")
