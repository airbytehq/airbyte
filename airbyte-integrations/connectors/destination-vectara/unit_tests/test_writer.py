#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import unittest
from unittest.mock import Mock

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, DestinationSyncMode, SyncMode
from destination_vectara.config import VectaraConfig
from destination_vectara.writer import VectaraWriter


class TestVectaraWriter(unittest.TestCase):
    def setUp(self):
        self.mock_config = VectaraConfig(
            **{
                "oauth2": {"client_id": "client_id", "client_secret": "client_secret"},
                "customer_id": "customer_id",
                "corpus_name": "corpus_name"
            }
        )

        def _request_side_effect(endpoint, data):
            if endpoint == "list-corpora":
                return {"corpus": []}
            if endpoint == "create-corpus":
                return {"corpusId": 999}
            if endpoint == "query":
                return {"responseSet": {"document": [{"id": 0}, {"id": 1}, {"id": 2}]}}
            if endpoint == "delete-doc":
                return {}
            if endpoint == "index":
                return {"status": {"code": "OK", "statusDetail": "sample status detail"}}
            return dict()
        
        self._request_side_effect = _request_side_effect

        self.vectara_indexer = VectaraWriter(self.mock_config)
        self.vectara_indexer._get_jwt_token = Mock()
        self.vectara_indexer.jwt_token = Mock()
        self.vectara_indexer.jwt_token_expires_ts = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc).timestamp()
        self.vectara_indexer._request = Mock()
        self.vectara_indexer._request.side_effect = self._request_side_effect

        # self.mock_client = self.vectara_indexer._get_client()
        # self.mock_client.get_or_create_collection = Mock()
        # self.mock_collection = self.mock_client.get_or_create_collection()
        # self.vectara_indexer.client = self.mock_client
        # self.mock_client.get_collection = Mock()

    def test_invalid_oauth_credentials(self):
        self.vectara_indexer._get_jwt_token.return_value = None
        result = self.vectara_indexer.check()
        self.assertEqual(result, "Unable to get JWT Token. Confirm your Client ID and Client Secret.")

    def test_multiple_corpora_with_corpus_name(self):
        self.vectara_indexer._request.side_effect = None
        self.vectara_indexer._request.return_value = {"corpus": [{"id": 0, "name": "corpus_name"}, {"id": 1, "name": "corpus_name"}]}
        result = self.vectara_indexer.check()
        self.assertEqual(result, f"Multiple Corpora exist with name {self.mock_config.corpus_name}")

    def test_one_corpus_with_corpus_name(self):
        self.vectara_indexer._request.side_effect = None
        self.vectara_indexer._request.return_value = {"corpus": [{"id": 0, "name": "corpus_name"}]}
        result = self.vectara_indexer.check()
        self.assertEqual(self.vectara_indexer.corpus_id, 0)

    def test_no_corpus_with_corpus_name(self):
        result = self.vectara_indexer.check()
        self.assertEqual(self.vectara_indexer.corpus_id, 999)

    def test_check_handles_failure_conditions(self):
        self.vectara_indexer._request.side_effect = Exception("Random exception")
        result = self.vectara_indexer.check()
        self.assertTrue("Random exception" in result)

    def test_pre_sync_calls_delete(self):
        self.vectara_indexer.check()
        self.vectara_indexer.pre_sync(
            Mock(
                streams=[
                    Mock(
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        stream=AirbyteStream(name="some_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                    )
                ]
            )
        )

        self.vectara_indexer._request.assert_any_call(endpoint="delete-doc", data={"customerId": self.mock_config.customer_id, "corpusId": self.vectara_indexer.corpus_id, "documentId": 0})
        self.vectara_indexer._request.assert_any_call(endpoint="delete-doc", data={"customerId": self.mock_config.customer_id, "corpusId": self.vectara_indexer.corpus_id, "documentId": 1})
        self.vectara_indexer._request.assert_any_call(endpoint="delete-doc", data={"customerId": self.mock_config.customer_id, "corpusId": self.vectara_indexer.corpus_id, "documentId": 2})

    def test_pre_sync_does_not_call_delete(self):
        self.vectara_indexer.pre_sync(
            Mock(streams=[Mock(destination_sync_mode=DestinationSyncMode.append, stream=Mock(name="some_stream"))])
        )

        self.vectara_indexer._request.assert_not_called()

    def test_delete_calls_delete(self):
        self.vectara_indexer.check()
        self.vectara_indexer.delete([0, 1, 2], None, "some_stream")

        self.vectara_indexer._request.assert_any_call(endpoint="delete-doc", data={"customerId": self.mock_config.customer_id, "corpusId": self.vectara_indexer.corpus_id, "documentId": 0})
        self.vectara_indexer._request.assert_any_call(endpoint="delete-doc", data={"customerId": self.mock_config.customer_id, "corpusId": self.vectara_indexer.corpus_id, "documentId": 1})
        self.vectara_indexer._request.assert_any_call(endpoint="delete-doc", data={"customerId": self.mock_config.customer_id, "corpusId": self.vectara_indexer.corpus_id, "documentId": 2})

    def test_index_calls_index(self):
        self.vectara_indexer.corpus_id = 0
        result = self.vectara_indexer.index([Mock(metadata={"key": "value"}, page_content="some content", embedding=[1, 2, 3])], None, "some_stream")

        print(result)

        self.vectara_indexer._request.assert_called_once()
