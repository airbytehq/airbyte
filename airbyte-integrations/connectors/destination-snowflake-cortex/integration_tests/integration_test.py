#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_snowflake_cortex.destination import DestinationSnowflakeCortex
from destination_snowflake_cortex.indexer import SnowflakeCortexIndexer
from langchain.embeddings import OpenAIEmbeddings
from snowflake import connector


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
                    "host": "MYACCOUNT",
                    "role": "MYUSERNAME",
                    "warehouse": "MYWAREHOUSE", 
                    "database": "MYDATABASE",
                    "default_schema": "MYSCHEMA",
                    "username": "MYUSERNAME",
                    "credentials": {
                        "password": "xxxxxxx"
                    }
                },
            },
        )
        assert outcome.status == Status.FAILED

    def _get_db_connection(self):
        return connector.connect(
            account=self.config["indexing"]["host"],
            role=self.config["indexing"]["role"],
            warehouse=self.config["indexing"]["warehouse"],
            database=self.config["indexing"]["database"],
            schema=self.config["indexing"]["default_schema"],
            user=self.config["indexing"]["username"],
            password=self.config["indexing"]["credentials"]["password"],
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

    def _run_cosine_similarity(self, query_vector, table_name):
        conn = self._get_db_connection()
        cursor = conn.cursor()

        query = f"""
        SELECT DOCUMENT_CONTENT
        FROM {table_name}
        ORDER BY VECTOR_L2_DISTANCE(
            CAST({query_vector} AS VECTOR(FLOAT, 1536)),
            embedding
        )
        LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
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

        # subsequent sync with append_dedup
        append_dedup_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup) 
        list(destination.write(self.config, append_dedup_catalog, [self._record("mystream", "Cats are nice too", 4), first_state_message]))
        assert(self._get_record_count("mystream") == 6)
        
        # comment the following so we can use fake for testing
        # embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        # result = self._run_cosine_similarity(embeddings.embed_query("feline animals"), "mystream")
        # assert(len(result) == 1)
        # result[0] == "str_col: Cats are nice"

   
    def test_overwrite_mode_deletes_records(self):  
        self._delete_table("mystream")
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(4)]

        # initial sync with replace 
        destination = DestinationSnowflakeCortex()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert(self._get_record_count("mystream") == 4)

        # following should replace existing records
        append_catalog = self._get_configured_catalog(DestinationSyncMode.overwrite) 
        list(destination.write(self.config, append_catalog, [self._record("mystream", "Cats are nice", 6), first_state_message]))
        assert(self._get_record_count("mystream") == 1)

    """
    Following tests are not code specific, but are useful to confirm that the Cortex functions are available and behaving as expcected
    """

    def test_cortex_functions_available(self):
        conn = self._get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
            $$Apple Vision Pro comprises approximately 300 components.[40] It has a curved laminated glass display on the front, an aluminum frame on its sides, a flexible cushion on the inside, and a removable, adjustable headband. The frame contains five sensors, six microphones, and 12 cameras.$$,
            'How many cameras are there on the product?'
        ) AS answer
        """
        try:
            cursor.execute(query)
        except Exception as e:
            self.fail(f"Cortex functions might not be available in database: {e}")

    def test_get_embeddings_using_cortex(self):
        conn = self._get_db_connection()
        cur = conn.cursor()
        document_content_list = ["dogs are number 1", "dogs are number 2", "cats are nummber 1"]

        cur.execute("""
        CREATE TEMPORARY TABLE temp_document_content (
            document_content STRING
        )
        """)
        cur.executemany("INSERT INTO temp_document_content (document_content) VALUES (%s)", document_content_list)

        cur.execute("""
        SELECT snowflake.cortex.embed_text('e5-base-v2', document_content) AS embedding
        FROM temp_document_content
        """)
        processed_data = cur.fetchall()
        self.assertTrue(processed_data, "No data found in the database")
        cur.execute("DROP TABLE temp_document_content")
        cur.close()
        conn.close()



