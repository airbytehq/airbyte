#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_snowflake_cortex.indexer import SnowflakeCortexIndexer
from destination_snowflake_cortex.destination import DestinationSnowflakeCortex
from snowflake import connector
from langchain.embeddings import OpenAIEmbeddings

class SnowflakeCortexIntegrationTest(BaseIntegrationTest):
    def _init_snowflake_cortex(self):
        pass

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._init_snowflake_cortex()

    def tearDown(self):
        pass

    def test_check_valid_config(self):
        outcome = DestinationSnowflakeCortex().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        outcome = DestinationSnowflakeCortex().check(
            logging.getLogger("airbyte"),
            {
                "processing": {"text_fields": ["str_col"], "chunk_size": 1000, "metadata_fields": ["int_col"]},
                "embedding": {"mode": "openai", "openai_key": "mykey"},
                "indexing": {
                    "account": "myaccount",
                    "username": "myaccount",
                    "password": "xxxxxxxxxxxx",
                    "database": "INTEGRATION_TEST",
                    "warehouse": "INTEGRATION_TEST_WAREHOUSE",
                    "role": "ACCOUNTADMIN"
                },
            },
        )
        assert outcome.status == Status.FAILED

    def _get_db_connection(self):
        return connector.connect(
            user=self.config["indexing"]["username"],
            password=self.config["indexing"]["password"],
            account=self.config["indexing"]["account"],
            warehouse=self.config["indexing"]["warehouse"],
            database=self.config["indexing"]["database"],
            role=self.config["indexing"]["role"],
            schema="airbyte_raw",
        )
    
    def _get_record_count(self, table_name):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0]

    def _delete_table(self, table_name):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        conn.close()

    def test_cortex_functions_available(self):
        # Create a cursor object
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Execute the query
        query = """
        SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
            $$Apple Vision Pro comprises approximately 300 components.[40] It has a curved laminated glass display on the front, an aluminum frame on its sides, a flexible cushion on the inside, and a removable, adjustable headband. The frame contains five sensors, six microphones, and 12 cameras.$$,
            'How many cameras are there on the product?'
        ) AS answer
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            print("Answer:", result[0])
        cursor.close()
        conn.close()

    def test_get_embeddings_from_documents(self):
        conn = self._get_db_connection()
        cur = conn.cursor()
        page_content_list = ["dogs are number 1", "dogs are number 2", "cats are nummber 1"]

        # Create a temporary table
        cur.execute("""
        CREATE TEMPORARY TABLE temp_page_content (
            page_content STRING
        )
        """)
        # Insert data into the temporary table
        cur.executemany("INSERT INTO temp_page_content (page_content) VALUES (%s)", page_content_list)

        # Process the data (for example, call a UDF or perform calculations)
        # Here we're just selecting the processed data as an example
        cur.execute("""
        SELECT snowflake.cortex.embed_text('e5-base-v2', page_content) AS embedding
        FROM temp_page_content
        """)
        processed_data = cur.fetchall()
        #for row in processed_data:
        #    print(row[0])
        cur.execute("DROP TABLE temp_page_content")
        cur.close()
        conn.close()

    def _run_cosine_similarity(self, query_vector, table_name):
       # Create a cursor object
        conn = self._get_db_connection()
        cursor = conn.cursor()

        query = f"""
        SELECT PAGE_CONTENT
        FROM {table_name}
        ORDER BY VECTOR_L2_DISTANCE(
            CAST({query_vector} AS VECTOR(FLOAT, 1536)),
            embedding
        )
        LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        # Close cursor and connection
        cursor.close()
        conn.close()
        return result

    def test_write(self):
        self._delete_table("mystream")
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync with replace 
        destination = DestinationSnowflakeCortex()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert(self._get_record_count("mystream") == 5)
    
        # subsequent sync with append
        append_catalog = self._get_configured_catalog(DestinationSyncMode.append) 
        list(destination.write(self.config, append_catalog, [self._record("mystream", "Cats are nice", 6), first_state_message]))
        assert(self._get_record_count("mystream") == 6)

        # todo: test merge once merge works in PyAirbyte 
        # perform a query using OpenAI embedding 
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        result = self._run_cosine_similarity(embeddings.embed_query("feline animals"), "mystream")
        assert(len(result) == 1)
        result[0] == "str_col: Cats are nice"

