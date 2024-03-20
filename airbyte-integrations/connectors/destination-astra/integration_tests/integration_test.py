#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from airbyte_cdk.destinations.vector_db_based.embedder import create_from_config
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_astra.astra_client import AstraClient
from destination_astra.config import ConfigModel
from destination_astra.destination import DestinationAstra


class AstraIntegrationTest(BaseIntegrationTest):

    def test_check_valid_config(self):
        outcome = DestinationAstra().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        invalid_config = self.config 

        invalid_config["embedding"]["openai_key"] = 123

        outcome = DestinationAstra().check(
            logging.getLogger("airbyte"), invalid_config)
        assert outcome.status == Status.FAILED

    def test_write(self):
        db_config = ConfigModel.parse_obj(self.config)
        embedder = create_from_config(db_config.embedding, db_config.processing)
        db_creds = db_config.indexing
        astra_client = AstraClient(
            db_creds.astra_db_endpoint, 
            db_creds.astra_db_app_token, 
            db_creds.astra_db_keyspace, 
            embedder.embedding_dimensions, 
            "cosine"
        )

        astra_client.delete_documents(collection_name=db_creds.collection, filter={})
        assert astra_client.count_documents(db_creds.collection) == 0

        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)

        message1 = self._record("mystream", "text data 1", 1)
        message2 = self._record("mystream", "text data 2", 2)

        outcome = list(DestinationAstra().write(self.config, catalog, [message1, message2]))
        assert astra_client.count_documents(db_creds.collection) == 2

