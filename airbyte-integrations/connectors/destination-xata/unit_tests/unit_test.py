#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest

from xata.client import XataClient
from xata.helpers import BulkProcessor


class DestinationConnectorXataTestCase(unittest.TestCase):

    def test_request(self):
        xata = XataClient(db_url="https://unit_tests-mock.results-store.xata.sh/db/mock-db", api_key="mock-key")
        bp = BulkProcessor(xata, thread_pool_size=1, batch_size=2, flush_interval=1)
        stats = bp.get_stats()

        assert "total" in stats
        assert "queue" in stats
        assert "failed_batches" in stats
        assert "tables" in stats

        assert stats["total"] == 0
        assert stats["queue"] == 0
        assert stats["failed_batches"] == 0


if __name__ == '__main__':
    unittest.main()
