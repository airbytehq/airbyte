#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import time
from typing import Any, Iterator, Mapping, Optional

from airbyte_cdk.logger import AirbyteLogger
from sumologic import SumoLogic


class Client:
    """Wrapper of sumologic python sdk"""

    logger: AirbyteLogger = AirbyteLogger()

    def __init__(self, access_id, access_key):
        self.sumo = SumoLogic(access_id, access_key)

    def check(self):
        # Make sure the client has correct access info.
        # 0 is an invalid search job ID in sumo-logic.
        invalid_job_id = 0
        resp = self.sumo.session.get(self.sumo.endpoint + f"/search/jobs/{invalid_job_id}")
        # If has permission to search job API, it will respond 404, invalid job id.
        # If access_id or access_key are invalid, this call will respond 401.
        if resp.status_code == 404:
            return True
        else:
            resp.raise_for_status()

    def search(
        self,
        query: str,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        limit: int = 10000,
        offset: int = 0,
        time_zone: str = "UTC",
        by_receipt_time: bool = True,
    ) -> Iterator[Mapping[str, Any]]:

        self.logger.info(f"Creating search job: {query}, from: {from_time}, to: {to_time}")
        search_job: dict = self.sumo.search_job(
            query,
            from_time,
            to_time,
            time_zone,
            by_receipt_time,
        )

        status: dict = self._wait_for_search_job(search_job)
        return self._read_messages(search_job, status, limit, offset)

    def _wait_for_search_job(self, search_job: dict, delay: int = 5, timeout=28800) -> dict:
        """Wait for search job to finish gathering results.

        While the search job is running you need to request the job status based on the search job ID.
        The API keeps the search job alive by either polling for status or gathering results.
        If the search job is not kept alive by API requests, it is canceled after five minutes.
        When a search job is canceled after five minutes of inactivity, you will get a 404 status.
        You must enable cookies for subsequent requests to the search job.
        A 404 status (Page Not Found) on a follow-up request may be due to a cookie not accompanying the request.
        There's a query timeout after eight hours (28800 seconds), even if the API is polling and making requests.
        If you are running very few queries, you may be able to go a little longer,
        but you can expect most of your queries to end after eight hours.
        """
        self.logger.info("Waiting for search job to be ready...")
        waittime: int = 0
        status: dict = self.sumo.search_job_status(search_job)
        # Possible state values are:
        #   - NOT STARTED
        #   - GATHERING RESULTS
        #   - FORCE PAUSED
        #   - DONE GATHERING RESULTS
        #   - CANCELLED
        # https://help.sumologic.com/APIs/Search-Job-API/About-the-Search-Job-API#sample-session-1
        while status["state"] != "DONE GATHERING RESULTS":
            if status["state"] == "CANCELLED":
                self.logger.warning("Search job status: CANCELLED.")
                break
            time.sleep(delay)
            waittime += delay
            if waittime > timeout:
                raise Exception(f"Reached query timeout {waittime}/{timeout}.")
            status = self.sumo.search_job_status(search_job)

        self.logger.info(f"Search job status: {status.get('state')}")
        return status

    def _read_messages(
        self,
        search_job: dict,
        status: dict,
        limit: int,
        offset: int,
    ) -> Iterator[Mapping[str, Any]]:
        total = status["messageCount"]
        limit = total if total < limit and total != 0 else limit  # compensate bad limit check
        count = 0

        # pagination logic
        self.logger.info(f"Start downloading {total} messages...")
        while offset < total:
            response = self.sumo.search_job_messages(search_job, limit=limit, offset=offset)
            offset += limit
            count += limit
            for msg in response["messages"]:
                yield msg["map"]
            self.logger.debug(f"Messages downloaded: {min(count, total)}/{total}")

            # Sumo Logic API rate limit is 4 requests per second
            time.sleep(1 / 4)
