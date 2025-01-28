#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import shutil
import signal
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any, Optional

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_milvus.destination import DestinationMilvus
from destination_milvus.indexer import MilvusIndexer
from langchain.embeddings import FakeEmbeddings
from langchain.vectorstores import Milvus
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility


class MilvusIntegrationTest(BaseIntegrationTest):
    """Integration tests for the Milvus destination connector using a local Milvus instance.

    The test suite automatically manages a local Milvus container using the standalone_embed.sh script.
    Tests verify the connector's ability to:
    - Connect to a local Milvus instance
    - Validate configurations
    - Write records in different sync modes
    - Handle vector operations
    """

    def wait_for_milvus(self, timeout=60) -> bool:
        """Wait for Milvus to be ready."""
        logger = logging.getLogger("airbyte")
        
        def disconnect_if_connected():
            try:
                connections.disconnect("test_driver")
            except Exception:
                pass

        def check_container_health():
            try:
                result = subprocess.run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", "milvus-standalone"],
                    capture_output=True,
                    text=True
                )
                return "healthy" in result.stdout.lower()
            except Exception:
                return False

        start_time = time.time()
        while time.time() - start_time < timeout:
            if not check_container_health():
                logger.info("Waiting for container to become healthy...")
                time.sleep(2)
                continue

            try:
                logger.info("Container is healthy, attempting to connect...")
                disconnect_if_connected()
                
                # Create new connection with explicit timeout and retries
                logger.info(f"Attempting connection to {self.config['indexing']['host']} with alias test_driver")
                try:
                    connections.connect(
                        alias="test_driver",
                        uri=self.config["indexing"]["host"],
                        timeout=10.0,
                        num_retries=5,
                        retry_interval=2.0
                    )
                    logger.info("Connection established successfully")
                except Exception as e:
                    logger.error(f"Connection failed with error: {str(e)}")
                    raise
                
                # Test connection by listing collections
                logger.info("Connection established, checking collections...")
                collections = utility.list_collections(using="test_driver")
                logger.info(f"Successfully listed collections: {collections}")
                return True
                
            except Exception as e:
                logger.warning(f"Connection attempt failed: {str(e)}")
                time.sleep(2)
                disconnect_if_connected()
                    
        logger.error("Milvus connection timed out after %d seconds", timeout)
        return False

    def _init_milvus(self):
        """Initialize connection to local Milvus instance."""
        if not self.wait_for_milvus():
            raise Exception("Milvus failed to become ready within timeout")
            
        if utility.has_collection(self.config["indexing"]["collection"], using="test_driver"):
            utility.drop_collection(self.config["indexing"]["collection"], using="test_driver")

    @classmethod
    def setUpClass(cls):
        """Set up test resources including local Milvus instance."""
        import subprocess
        import time
        from pathlib import Path
        
        logger = logging.getLogger("airbyte")
        logger.info("Setting up test class...")
        
        # Force cleanup any existing containers
        try:
            subprocess.run(["docker", "rm", "-f", "milvus-standalone"], stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.warning(f"Initial container cleanup failed: {e}")
        
        # Start local Milvus using docker directly
        try:
            logger.info("Starting Milvus container...")
            # Use temporary directory for volumes
            import tempfile
            import shutil
            
            # Create a temporary directory for Milvus data
            tmp_dir = Path(tempfile.mkdtemp(prefix="milvus_test_"))
            logger.info(f"Created temporary directory at {tmp_dir}")
            
            # Create config directory and copy config file
            config_dir = tmp_dir / "configs"
            config_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(
                Path(__file__).parent / "milvus.yaml",
                config_dir / "milvus.yaml"
            )
            
            # Create data directory
            data_dir = tmp_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Store temp dir path for cleanup
            cls.tmp_dir = tmp_dir
            
            # Start etcd container first
            subprocess.run([
                "docker", "run", "-d",
                "--name", "milvus-etcd",
                "-p", "2379:2379",
                "-e", "ALLOW_NONE_AUTHENTICATION=yes",
                "-e", "ETCD_ADVERTISE_CLIENT_URLS=http://0.0.0.0:2379",
                "-e", "ETCD_LISTEN_CLIENT_URLS=http://0.0.0.0:2379",
                "bitnami/etcd:latest"
            ], check=True)
            
            # Wait for etcd to be ready
            time.sleep(5)
            
            # Start Milvus container with proper volume mounts and standalone command
            subprocess.run([
                "docker", "run", "-d",
                "--name", "milvus-standalone",
                "--link", "milvus-etcd:etcd",
                "-p", "19530:19530",
                "-p", "9091:9091",
                "-v", f"{data_dir.absolute()}:/var/lib/milvus/db",
                "-v", f"{config_dir.absolute()}:/milvus/configs",
                "-e", "ETCD_ENDPOINTS=etcd:2379",
                "--health-cmd", "curl -f http://localhost:9091/healthz || exit 1",
                "--health-interval", "5s",
                "--health-timeout", "10s",
                "--health-retries", "3",
                "milvusdb/milvus:v2.5.4",
                "milvus", "run", "standalone"
            ], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Milvus container: {e}")
            raise
            
        # Wait for container to be healthy
        logger.info("Waiting for container to be healthy...")
        max_retries = 30
        while max_retries > 0:
            try:
                result = subprocess.run(
                    ["docker", "inspect", "--format", "{{.State.Health.Status}}", "milvus-standalone"],
                    capture_output=True,
                    text=True
                )
                if "healthy" in result.stdout.lower():
                    logger.info("Container is healthy")
                    break
            except Exception as e:
                logger.warning(f"Health check failed: {e}")
            max_retries -= 1
            time.sleep(2)
            
        if max_retries == 0:
            raise Exception("Container failed to become healthy")
            
        logger.info("Test class setup complete")

    def setUp(self):
        """Set up test instance."""
        logger = logging.getLogger("airbyte")
        logger.info("Setting up test instance...")
        
        # Load config
        config_path = Path(__file__).parent / "secrets/config.json"
        if not config_path.exists():
            config_path = Path("secrets/config.json")
            
        with open(config_path, "r") as f:
            self.config = json.loads(f.read())
            
        # Ensure config points to local instance
        self.config["indexing"]["host"] = "http://127.0.0.1:19530"
        self.config["indexing"]["auth"] = {"mode": "no_auth"}
        
        # Initialize Milvus connection
        if not self.wait_for_milvus(timeout=30):
            raise Exception("Failed to connect to Milvus")

    def test_check_valid_config(self):
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def _create_collection(self, vector_dimensions=1536):
        pk = FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True)
        vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dimensions)
        schema = CollectionSchema(fields=[pk, vector], enable_dynamic_field=True)
        collection = Collection(name=self.config["indexing"]["collection"], schema=schema, using="test_driver")
        collection.create_index(
            field_name="vector", index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        )

    def test_check_valid_config_pre_created_collection(self):
        self._create_collection()
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config_vector_dimension(self):
        self._create_collection(vector_dimensions=666)
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.FAILED

    def test_check_invalid_config(self):
        """Test that invalid configuration fails quickly."""
        logger = logging.getLogger("airbyte")
        logger.info("Starting invalid config test...")
        
        # Use TEST-NET-1 address (RFC 5737) for guaranteed failure
        invalid_config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "fake", "dimensions": 1536},
            "indexing": {
                "host": "http://192.0.2.1:19530",  # TEST-NET-1 address for quick failure
                "collection": "test2",
                "auth": {"mode": "no_auth"},
                "vector_field": "vector",
                "text_field": "text",
            },
        }
        
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def timeout_handler(seconds):
            def signal_handler(signum, frame):
                raise TimeoutError(f"Operation timed out after {seconds} seconds")
            
            # Set up the timeout
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                # Disable the alarm
                signal.alarm(0)
        
        start_time = time.time()
        logger.info("Running check with invalid config...")
        
        try:
            with timeout_handler(3):  # Shorter timeout for invalid config
                outcome = DestinationMilvus().check(logger, invalid_config)
        except TimeoutError as e:
            logger.error(f"Check timed out: {e}")
            outcome = None
        except Exception as e:
            logger.error(f"Check failed with error: {e}")
            outcome = None
            
        elapsed_time = time.time() - start_time
        logger.info(f"Check completed in {elapsed_time:.2f} seconds")
        
        assert outcome is not None, "Check operation failed to complete"
        assert outcome.status == Status.FAILED, "Expected check to fail with invalid config"
        assert elapsed_time < 4, f"Test took too long: {elapsed_time:.2f} seconds"

    def tearDown(self):
        """Clean up test instance resources."""
        logger = logging.getLogger("airbyte")
        logger.info("Cleaning up test instance...")
        
        try:
            connections.disconnect("test_driver")
        except Exception as e:
            logger.warning(f"Failed to disconnect from Milvus: {e}")
            
    @classmethod
    def tearDownClass(cls):
        """Clean up test class resources."""
        logger = logging.getLogger("airbyte")
        logger.info("Cleaning up test class...")
        
        try:
            # Force cleanup
            subprocess.run(["docker", "rm", "-f", "milvus-standalone"], check=True)
            logger.info("Successfully cleaned up Milvus container")
        except Exception as e:
            logger.error(f"Failed to clean up Milvus container: {e}")
            # Don't raise, as we want to continue with other cleanup
            
        # Clean up temporary directory
        try:
            if hasattr(cls, 'tmp_dir'):
                shutil.rmtree(cls.tmp_dir)
                logger.info("Successfully cleaned up temporary directory")
        except Exception as e:
            logger.error(f"Failed to clean up temporary directory: {e}")

    def test_indexer_operations(self):
        """Test MilvusIndexer operations directly."""
        self._init_milvus()
        
        # Test indexer initialization
        indexer = MilvusIndexer(self.config, OPEN_AI_VECTOR_SIZE)
        
        # Test write operation with various record formats
        records = [
            {
                "text": "Test text 1",
                "vector": [0.1] * OPEN_AI_VECTOR_SIZE,
                "_ab_record_id": "test_1",
                "metadata": {"category": "test"}
            },
            {
                "text": "Test text 2",
                "vector": [0.2] * OPEN_AI_VECTOR_SIZE,
                "_ab_record_id": "test_2",
                "metadata": {"category": "test"}
            }
        ]
        indexer.write(records)
        
        # Test search operation with different parameters
        results = indexer.search([0.1] * OPEN_AI_VECTOR_SIZE, 1)
        assert len(results) == 1
        assert "_ab_record_id" in results[0]
        assert "metadata" in results[0]
        assert results[0]["metadata"]["category"] == "test"
        
        # Test search with limit > 1
        results = indexer.search([0.1] * OPEN_AI_VECTOR_SIZE, 2)
        assert len(results) == 2
        
        # Test search with expr filter
        results = indexer.search(
            [0.1] * OPEN_AI_VECTOR_SIZE,
            2,
            expr='metadata["category"] == "test"'
        )
        assert len(results) == 2
        
        # Test delete operation
        indexer.delete(["test_1"])
        results = indexer.search([0.1] * OPEN_AI_VECTOR_SIZE, 1)
        assert results[0]["_ab_record_id"] != "test_1"
        
        # Test batch write with larger dataset
        large_batch = []
        for i in range(10):
            large_batch.append({
                "text": f"Batch text {i}",
                "vector": [float(i)/10] * OPEN_AI_VECTOR_SIZE,
                "_ab_record_id": f"batch_{i}",
                "metadata": {"batch": i}
            })
        indexer.write(large_batch)
        
        # Test collection exists after write
        assert utility.has_collection(self.config["indexing"]["collection"], using="test_driver")
        
        # Test error handling
        with self.assertRaises(Exception):
            indexer.write([{"invalid": "record"}])
            
        # Test invalid vector dimension
        with self.assertRaises(Exception):
            invalid_record = {
                "text": "Invalid vector",
                "vector": [0.1] * (OPEN_AI_VECTOR_SIZE + 1),
                "_ab_record_id": "invalid"
            }
            indexer.write([invalid_record])
            
        # Test connection error handling
        with self.assertRaises(Exception):
            bad_config = self.config.copy()
            bad_config["indexing"]["host"] = "http://invalid:19530"
            bad_indexer = MilvusIndexer(bad_config, OPEN_AI_VECTOR_SIZE)
            bad_indexer.write(records)
            
    def test_write(self):
        """Test writing records in different sync modes."""
        self._init_milvus()
        
        # Test overwrite mode
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        destination = DestinationMilvus()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        collection = Collection(self.config["indexing"]["collection"], using="test_driver")
        collection.flush()
        assert len(collection.query(expr="pk != 0")) == 5

        # Test append mode
        append_catalog = self._get_configured_catalog(DestinationSyncMode.append)
        append_records = [self._record("mystream", f"Cats are number {i}", i + 5) for i in range(3)]
        list(destination.write(self.config, append_catalog, [*append_records, first_state_message]))
        collection.flush()
        assert len(collection.query(expr="pk != 0")) == 8

        # Test append_dedup mode with update
        dedup_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        update_record = self._record("mystream", "Updated cat", 7)  # Update one of the append records
        list(destination.write(self.config, dedup_catalog, [update_record, first_state_message]))
        collection.flush()

        # Verify update
        result = collection.search(
            anns_field=self.config["indexing"]["vector_field"],
            param={},
            data=[[0] * OPEN_AI_VECTOR_SIZE],
            limit=10,
            expr='_ab_record_id == "mystream_7"',
            output_fields=["text"],
        )
        assert len(result[0]) == 1
        assert result[0][0].entity.get("text") == "str_col: Updated cat"

        # Test error handling with invalid record
        with self.assertRaises(Exception):
            invalid_record = {"stream": "mystream", "data": {"invalid": "data"}}
            list(destination.write(self.config, catalog, [{"type": "RECORD", "record": invalid_record}]))

        # Test batch processing
        large_chunk = [self._record("mystream", f"Batch record {i}", i + 100) for i in range(50)]
        list(destination.write(self.config, append_catalog, [*large_chunk, first_state_message]))
        collection.flush()
        assert len(collection.query(expr="pk != 0")) > 50  # Previous records + batch records

        # test langchain integration with local instance
        from langchain.embeddings import FakeEmbeddings
        embeddings = FakeEmbeddings(size=self.config["embedding"]["dimensions"])
        vs = Milvus(
            embedding_function=embeddings,
            collection_name=self.config["indexing"]["collection"],
            connection_args={"uri": self.config["indexing"]["host"]},
            text_field=self.config["indexing"]["text_field"],  # Use configured text field
        )
        
        # Ensure fields are properly set up
        collection = Collection(self.config["indexing"]["collection"], using="test_driver")
        collection.load()
        
        # Get actual field names from collection schema
        schema = collection.schema
        field_names = [field.name for field in schema.fields]
        
        # Add available fields
        for field in ["text", "_ab_record_id"]:
            if field in field_names:
                vs.fields.append(field)

        result = vs.similarity_search("feline animals", 1, search_params={"output_fields": ["text", "_ab_record_id"]})
        assert result[0].metadata["_ab_record_id"] == "mystream_2"
