# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import gc
import os
import unittest
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

from .server import SpecmaticServer


class SpecmaticIntegrationTestCase(unittest.TestCase):
    # Port to run Specmatic on
    specmatic_port: int = 9000
    specmatic_host: str = "127.0.0.1"

    # Shared server instance across test classes
    _shared_server: Optional[SpecmaticServer] = None
    _server: Optional[SpecmaticServer] = None
    config: Dict[str, Any] = {}
    source: Optional[YamlDeclarativeSource] = None

    @classmethod
    def setUpClass(cls):
        # Resolve repository paths relative to this file
        current_file = Path(__file__).resolve()
        # Find repo root dynamically by scanning parent directories for specmatic_test/specs/stripe-official.json
        repo_root = None
        for parent in current_file.parents:
            if (parent / "specmatic_test" / "specs" / "stripe-official.json").exists():
                repo_root = parent
                break
        if not repo_root:
            repo_root = current_file.parents[5]  # Fallback: airbyte-master

        # Determine if we are running inside Docker
        is_docker = os.path.exists("/.dockerenv")
        cls.specmatic_host = "host.docker.internal" if is_docker else "127.0.0.1"

        # Configure url_base for the connector config
        cls.config = {"url_base": f"http://{cls.specmatic_host}:{cls.specmatic_port}/v1/"}

        # Start shared server if not already started
        if SpecmaticIntegrationTestCase._shared_server is None:
            server = SpecmaticServer(port=cls.specmatic_port, host=cls.specmatic_host)
            server.start(repo_root=repo_root)
            SpecmaticIntegrationTestCase._shared_server = server
            import atexit

            atexit.register(server.stop)
        cls._server = SpecmaticIntegrationTestCase._shared_server

    @classmethod
    def tearDownClass(cls):
        # Keep server running for subsequent test classes; atexit will shut it down cleanly at process exit.
        pass

    def setUp(self) -> None:
        super().setUp()
        # Force garbage collection to release any dangling SQLite file handles
        gc.collect()
        # Explicitly delete the SQLite cache file to prevent cache leakage between tests
        cache_file = Path(__file__).resolve().parent.parent / "test_cache.sqlite"
        if cache_file.exists():
            try:
                os.remove(cache_file)
                print(f"Successfully deleted cache file {cache_file} in setUp.")
            except Exception as e:
                print(f"Could not remove SQLite cache file in setUp: {e}")

    def tearDown(self) -> None:
        # Uninstall and clear requests_cache to release SQLite file handles on Windows
        import requests_cache

        try:
            if self.source:
                for stream in self.source.streams(config=self.config):
                    if hasattr(stream, "retriever") and hasattr(stream.retriever, "requester"):
                        session = getattr(stream.retriever.requester, "_session", None)
                        if session:
                            session.close()
        except Exception as e:
            print(f"Error closing stream session in Specmatic tearDown: {e}")

        try:
            requests_cache.clear()
            requests_cache.uninstall_cache()
        except Exception:
            pass

        # Force garbage collection to release all database connection file handles
        gc.collect()

        cache_file = Path(__file__).resolve().parent.parent / "test_cache.sqlite"
        if cache_file.exists():
            try:
                os.remove(cache_file)
                print(f"Successfully deleted cache file {cache_file} in tearDown.")
            except Exception as e:
                print(f"Could not remove SQLite cache file in tearDown: {e}")

    def assert_contract_read_success(self, output: Any) -> None:
        """Validate that an Airbyte stream read executed against Specmatic mock without contract or runtime errors."""
        self.assertEqual(getattr(output, "errors", []), [], f"Stream read produced errors: {getattr(output, 'errors', [])}")

    def set_specmatic_expectation(
        self, path: str, query: Dict[str, str], response_body: Union[Dict[str, Any], list], method: str = "GET", status_code: int = 200
    ) -> None:
        """
        [Legacy / Manual Mocking] Register dynamic expectations with the Specmatic mock server.
        Prefer Zero-Hardcoding Specmatic testing where responses are auto-generated from OpenAPI definitions.
        """
        url = f"http://{self.specmatic_host}:{self.specmatic_port}/_specmatic/expectations"
        payload = {
            "http-request": {"method": method, "path": path, "query": query},
            "http-response": {"status": status_code, "body": response_body},
        }
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to set Specmatic expectation: {resp.status_code} - {resp.text}")

