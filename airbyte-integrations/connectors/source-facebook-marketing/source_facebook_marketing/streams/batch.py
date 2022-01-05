import logging
from typing import Optional, Iterable, List, MutableMapping, Any

import pendulum
from facebook_business.api import FacebookResponse, FacebookAdsApiBatch, FacebookRequest

logger = logging.getLogger("airbyte")

class BatchExecutor:
    """ Execute all pending requests in batch (max size is N)
    Retry empty responses
    Retry failed requests
    Return responses upon

    """
    MAX_BATCH_SIZE = 50

    def __init__(self, api, size: int = MAX_BATCH_SIZE):
        self._api = api
        self._max_batch_size = size
        self._batch: FacebookAdsApiBatch = self._api.api.new_batch()

    def on_success(self, response: FacebookResponse):
        # logger.info("GOT data, headers=%s, paging=%s", response.headers(), response.json()["paging"])
        # records.append(response.json()["data"])
        for record in response.json()["data"]:
            ad_ids.add(record["ad_id"])
            records.append({"record": 1, "date_start": record["date_start"], "ad_id": record["ad_id"]})

    def on_failure(self, response: FacebookResponse):
        logger.info(f"Request failed with response: {response.body()}")

    def execute_in_batch(self, pending_requests: Iterable[FacebookRequest]) -> List[List[MutableMapping[str, Any]]]:
        """Execute list of requests in batches"""
        records = []
        for request in pending_requests:
            self._batch.add_request(request, success=self.on_success, failure=self.on_failure)

        while self._batch:
            logger.info(f"Batch starting: {pendulum.now()}")
            api_batch = self._batch.execute()
            logger.info(f"Batch executed: {pendulum.now()}")
            if api_batch:
                logger.info("Retry failed requests in batch")

        return records


class AsyncExecutor:
    def __init__(self):
        pass

    def execute(self, jobs: List[AsyncJob]):
        pass
