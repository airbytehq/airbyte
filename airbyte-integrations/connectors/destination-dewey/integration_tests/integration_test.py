#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""End-to-end smoke tests against the live Dewey API.

Reads credentials from env vars:

    DEWEY_API_KEY            required (dwy_live_... or dwy_test_...)
    DEWEY_TEST_COLLECTION_ID optional; if unset, the first collection in the org is used
    DEWEY_BASE_URL           optional; defaults to https://api.meetdewey.com/v1

Each test uses a uniquified stream name (`smoke_articles_<uuid>`) and tags every
uploaded document with that stream tag, so cleanup deletes only what the test wrote.
"""

import logging
import os
import time
import unittest
import uuid
from typing import Any, Dict, List

from destination_dewey.client import PK_TAG_PREFIX, STREAM_TAG_PREFIX, DeweyClient
from destination_dewey.config import DeweyConfig
from destination_dewey.destination import DestinationDewey

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


DEFAULT_BASE_URL = os.environ.get("DEWEY_BASE_URL", "https://api.meetdewey.com/v1")


def _require_api_key() -> str:
    key = os.environ.get("DEWEY_API_KEY")
    if not key:
        raise unittest.SkipTest("DEWEY_API_KEY env var not set; skipping live integration tests.")
    return key


def _record(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=int(time.time() * 1000)),
    )


def _state() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={}))


def _catalog(stream_name: str, sync_mode: DestinationSyncMode) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"type": "string"},
                            "body": {"type": "string"},
                            "author": {"type": "string"},
                        },
                    },
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                primary_key=[["id"]],
                sync_mode=SyncMode.incremental,
                destination_sync_mode=sync_mode,
            )
        ]
    )


def _resolve_collection_id(client: DeweyClient) -> str:
    explicit = os.environ.get("DEWEY_TEST_COLLECTION_ID")
    if explicit:
        return explicit
    collections = client._request("GET", "/collections")
    if not isinstance(collections, list) or not collections:
        raise unittest.SkipTest("No Dewey collections available — set DEWEY_TEST_COLLECTION_ID or create one in your project.")
    return collections[0]["id"]


class DeweySmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api_key = _require_api_key()
        cls.client = DeweyClient(DeweyConfig(api_key=cls.api_key, base_url=DEFAULT_BASE_URL))
        cls.collection_id = _resolve_collection_id(cls.client)
        # Uniquify stream name so parallel runs don't step on each other.
        cls.run_id = uuid.uuid4().hex[:8]
        cls.stream_name = f"smoke_articles_{cls.run_id}"
        cls.stream_id = f"default__{cls.stream_name}"
        cls.stream_tag = f"{STREAM_TAG_PREFIX}{cls.stream_id}"
        cls.config = {
            "api_key": cls.api_key,
            "base_url": DEFAULT_BASE_URL,
            "stream_collections": {cls.stream_id: cls.collection_id},
            "auto_create_collections": False,
            "text_fields": ["title", "body"],
            "title_field": "title",
            "metadata_fields": ["author"],
            "parallelize": False,
            "flush_interval": 50,
        }
        logging.getLogger("airbyte").info("Smoke run: collection=%s stream=%s", cls.collection_id, cls.stream_name)

    @classmethod
    def tearDownClass(cls):
        try:
            cls._cleanup_stream_docs()
        except Exception as e:  # pragma: no cover - cleanup
            logging.getLogger("airbyte").warning("Smoke teardown cleanup failed: %s", e)

    @classmethod
    def _cleanup_stream_docs(cls) -> None:
        ids: List[str] = cls.client.find_document_ids_by_tag(cls.collection_id, cls.stream_tag)
        if ids:
            cls.client.delete_documents(cls.collection_id, ids)

    def setUp(self):
        # Each test starts from a clean slate (within the shared collection).
        self._cleanup_stream_docs()

    # ---- tests ----------------------------------------------------------------

    def test_check_valid(self):
        result = DestinationDewey().check(logging.getLogger("airbyte"), self.config)
        self.assertEqual(result.status, Status.SUCCEEDED, msg=result.message)

    def test_check_invalid_api_key(self):
        bad = dict(self.config)
        bad["api_key"] = "dwy_live_obviously-invalid-key"
        result = DestinationDewey().check(logging.getLogger("airbyte"), bad)
        self.assertEqual(result.status, Status.FAILED)

    def test_write_then_dedup_replaces_prior_version(self):
        records = [
            {"id": 1, "title": f"Cats {self.run_id}", "body": "Cats are small carnivorous mammals.", "author": "ari"},
            {"id": 2, "title": f"Dogs {self.run_id}", "body": "Dogs are loyal companions.", "author": "ari"},
            {"id": 3, "title": f"Birds {self.run_id}", "body": "Birds have feathers.", "author": "sam"},
        ]
        catalog = _catalog(self.stream_name, DestinationSyncMode.append_dedup)
        messages = [_record(self.stream_name, r) for r in records] + [_state()]
        list(DestinationDewey().write(self.config, catalog, messages))

        ours = self._our_docs()
        self.assertEqual(len(ours), 3, msg=f"Expected 3 stream-tagged docs, got {len(ours)}: {[d['filename'] for d in ours]}")

        # Tags should reflect stream + primary key.
        for doc in ours:
            tags = doc.get("tags") or []
            self.assertIn(self.stream_tag, tags)
            self.assertTrue(any(t.startswith(PK_TAG_PREFIX) for t in tags), msg=f"missing pk tag: {tags}")

        # Update record id=2 — append_dedup should replace the old version, total stays 3.
        update = [
            _record(self.stream_name, {"id": 2, "title": f"Dogs revised {self.run_id}", "body": "Dogs are very loyal.", "author": "ari"}),
            _state(),
        ]
        list(DestinationDewey().write(self.config, catalog, update))
        ours = self._our_docs()
        self.assertEqual(len(ours), 3, msg=f"Expected 3 docs after dedup update, got {len(ours)}")
        revised = [d for d in ours if "revised" in (d.get("filename") or "")]
        self.assertEqual(len(revised), 1, msg=f"Expected one 'revised' doc, got: {[d['filename'] for d in ours]}")

    def test_overwrite_clears_prior_records(self):
        # Seed with one record under append mode.
        seed = [_record(self.stream_name, {"id": 99, "title": f"Seed {self.run_id}", "body": "to be wiped", "author": "ari"}), _state()]
        list(DestinationDewey().write(self.config, _catalog(self.stream_name, DestinationSyncMode.append), seed))
        self.assertGreaterEqual(len(self._our_docs()), 1)

        # Overwrite sync should delete every doc tagged with this stream, then upload a new set.
        new = [_record(self.stream_name, {"id": 100, "title": f"Fresh {self.run_id}", "body": "post-overwrite", "author": "ari"}), _state()]
        list(DestinationDewey().write(self.config, _catalog(self.stream_name, DestinationSyncMode.overwrite), new))
        ours = self._our_docs()
        self.assertEqual(len(ours), 1, msg=f"Expected 1 stream-tagged doc, got: {[d['filename'] for d in ours]}")
        self.assertTrue(ours[0]["filename"].startswith("Fresh-"))

    # ---- helpers --------------------------------------------------------------

    def _our_docs(self) -> List[Dict[str, Any]]:
        return [d for d in self.client.list_documents(self.collection_id) if self.stream_tag in (d.get("tags") or [])]


if __name__ == "__main__":
    unittest.main()
