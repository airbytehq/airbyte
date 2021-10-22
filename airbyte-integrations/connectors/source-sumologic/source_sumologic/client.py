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
        # Make sure the client has correct access info
        self.sumo.get_personal_folder()

    def search(
        self,
        query: str,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        limit: int = 10000,
        offset: int = 0,
        time_zone: str = "UTC",
        by_receipt_time: bool = False,
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

    def _wait_for_search_job(self, search_job: dict) -> dict:
        self.logger.info("Waiting for search job to be ready...")

        delay = 5
        status: dict = self.sumo.search_job_status(search_job)
        while status["state"] != "DONE GATHERING RESULTS":
            if status["state"] == "CANCELLED":
                self.logger.warning("Search job status: CANCELLED.")
                break
            time.sleep(delay)
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
