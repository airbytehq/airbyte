#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

# This file contains the longest unit tests. This spawns a local fauna container and
# tests against that. These tests are used to make sure we don't skip documents on
# certain edge cases.

import subprocess
import time
from datetime import datetime

import docker
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from faunadb import query as q
from source_fauna import SourceFauna
from test_util import CollectionConfig, DeletionsConfig, FullConfig, config, mock_logger, ref


def setup_database(source: SourceFauna):
    print("Setting up database...")
    source.client.query(
        q.create_collection(
            {
                "name": "foo",
            }
        )
    )
    # All these documents will have the same `ts`, so we need to make sure
    # that we don't skip any of these.
    db_results = source.client.query(
        q.do(
            [
                q.create(
                    ref(101, "foo"),
                    {
                        "data": {
                            "a": 5,
                        },
                    },
                ),
                q.create(
                    ref(102, "foo"),
                    {
                        "data": {
                            "a": 6,
                        },
                    },
                ),
                q.create(
                    ref(103, "foo"),
                    {
                        "data": {
                            "a": 7,
                        },
                    },
                ),
                q.create(
                    ref(104, "foo"),
                    {
                        "data": {
                            "a": 8,
                        },
                    },
                ),
            ]
        )
    )
    # Do this seperately, so that the above documents get added to this index.
    source.client.query(
        q.create_index(
            {
                "name": "foo_ts",
                "source": q.collection("foo"),
                "terms": [],
                "values": [
                    {"field": "ts"},
                    {"field": "ref"},
                ],
            }
        ),
    )
    print("Database is setup!")

    # Store all the refs and ts of the documents we created, so that we can validate them
    # below.
    db_data = {
        "ref": [],
        "ts": [],
    }
    for create_result in db_results:
        db_data["ref"].append(create_result["ref"])
        db_data["ts"].append(create_result["ts"])
    return db_data


def stop_container(container):
    print("Stopping FaunaDB container...")
    container.stop()
    print("Stopped FaunaDB container")


def setup_container():
    """Starts and stops a local fauna container"""
    client = docker.from_env()
    # Bind to port 9000, so that we can run these tests without stopping a local container
    container = client.containers.run(
        "fauna/faunadb",
        remove=True,
        ports={8443: 9000},
        detach=True,
    )
    print("Waiting for FaunaDB to start...")
    i = 0
    while i < 100:
        res = subprocess.run(
            [
                "curl",
                "-m",
                "1",
                "--output",
                "/dev/null",
                "--silent",
                "--head",
                "http://127.0.0.1:9000",
            ]
        )
        if res.returncode == 0:
            print("")
            break
        time.sleep(1)
        print(".", flush=True, end="")
        i += 1
    print("FaunaDB is ready! Starting tests")

    try:
        source = SourceFauna()
        # Port 9000, bound above
        source._setup_client(
            FullConfig(
                secret="secret",
                port=9000,
                domain="localhost",
                scheme="http",
            )
        )
        db_data = setup_database(source)
        return container, db_data, source
    except Exception:
        stop_container(container)
        raise


def run_add_removes_test(source: SourceFauna, logger, stream: ConfiguredAirbyteStream):
    source._setup_client(FullConfig.localhost())
    source.client.query(q.create(ref(105, "foo"), {"data": {"a": 10}}))
    deleted_ts = (
        source.client.query(
            q.do(
                q.delete(ref(105, "foo")),
                q.now(),
            )
        )
        .to_datetime()
        .timestamp()
        * 1_000_000
    )

    conf = CollectionConfig(
        deletions=DeletionsConfig.ignore(),
    )
    results = list(source.read_removes(logger, stream, conf, state={}, deletion_column="my_deletion_col"))
    assert len(results) == 1
    assert results[0]["ref"] == "105"
    assert results[0]["ts"] >= deleted_ts
    assert datetime.fromisoformat(results[0]["my_deletion_col"]).timestamp() * 1_000_000 >= deleted_ts


def run_removes_order_test(source: SourceFauna, logger, stream: ConfiguredAirbyteStream):
    source._setup_client(FullConfig.localhost())

    start = source.client.query(q.to_micros(q.now()))

    ref1 = source.client.query(q.select("ref", q.create(q.collection("foo"), {"data": {}})))
    ref2 = source.client.query(q.select("ref", q.create(q.collection("foo"), {"data": {}})))
    ref3 = source.client.query(q.select("ref", q.create(q.collection("foo"), {"data": {}})))

    # Delete in a different order than created
    source.client.query(q.delete(ref1))
    source.client.query(q.delete(ref3))
    source.client.query(q.delete(ref2))

    print(ref1, ref2, ref3)

    conf = CollectionConfig(
        deletions=DeletionsConfig.ignore(),
        page_size=2,
    )
    results = list(
        source.read_removes(
            logger,
            stream,
            conf,
            state={
                "ts": start - 1,
            },
            deletion_column="my_deletion_col",
        )
    )
    assert len(results) == 3
    # The order received should be the order deleted
    assert results[0]["ref"] == ref1.id()
    assert results[1]["ref"] == ref3.id()
    assert results[2]["ref"] == ref2.id()
    # Make sure the newest event is last in the list.
    assert results[0]["ts"] < results[1]["ts"]
    assert results[1]["ts"] < results[2]["ts"]


def run_general_remove_test(source: SourceFauna, logger):
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="deletions_test", json_schema={}, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[stream])
    source.client.query(
        q.create_collection(
            {
                "name": "deletions_test",
            }
        )
    )
    db_data = source.client.query(
        [
            q.create(
                ref(101, "deletions_test"),
                {
                    "data": {
                        "a": 5,
                    },
                },
            ),
            q.create(
                ref(102, "deletions_test"),
                {
                    "data": {
                        "a": 6,
                    },
                },
            ),
            q.create(
                ref(103, "deletions_test"),
                {
                    "data": {
                        "a": 7,
                    },
                },
            ),
            q.create(
                ref(104, "deletions_test"),
                {
                    "data": {
                        "a": 8,
                    },
                },
            ),
        ]
    )
    # Do this seperately, so that the above documents get added to this index.
    source.client.query(
        q.create_index(
            {
                "name": "deletions_test_ts",
                "source": q.collection("deletions_test"),
                "terms": [],
                "values": [
                    {"field": "ts"},
                    {"field": "ref"},
                ],
            }
        ),
    )
    conf = config(
        {
            "port": 9000,
            "collection": {
                "deletions": {"deletion_mode": "deleted_field", "column": "deleted_at"},
            },
        }
    )
    print("=== check: make sure we read the initial state")
    documents, state = read_records(source.read(logger, conf, catalog, {}), "deletions_test")
    assert documents == [
        {
            "ref": "101",
            "ts": db_data[0]["ts"],
            "data": {"a": 5},
            "ttl": None,
        },
        {
            "ref": "102",
            "ts": db_data[1]["ts"],
            "data": {"a": 6},
            "ttl": None,
        },
        {
            "ref": "103",
            "ts": db_data[2]["ts"],
            "data": {"a": 7},
            "ttl": None,
        },
        {
            "ref": "104",
            "ts": db_data[3]["ts"],
            "data": {"a": 8},
            "ttl": None,
        },
    ]

    print("=== check: make sure we don't produce more records when nothing changed")
    documents, state = read_records(source.read(logger, conf, catalog, state), "deletions_test")
    assert documents == []

    source.client.query(q.delete(ref(101, "deletions_test")))
    source.client.query(q.delete(ref(103, "deletions_test")))

    print("=== check: make sure deleted documents produce records")
    documents, state = read_records(source.read(logger, conf, catalog, state), "deletions_test")
    assert len(documents) == 2

    assert documents[0]["ref"] == "101"
    assert documents[0]["ts"] > db_data[0]["ts"]
    assert "data" not in documents[0]
    assert datetime.fromisoformat(documents[0]["deleted_at"]).timestamp() * 1_000_000 > db_data[0]["ts"]

    assert documents[1]["ref"] == "103"
    assert documents[1]["ts"] > db_data[2]["ts"]
    assert "data" not in documents[1]
    assert datetime.fromisoformat(documents[1]["deleted_at"]).timestamp() * 1_000_000 > db_data[2]["ts"]

    print("=== check: make sure we don't produce more deleted documents when nothing changed")
    documents, state = read_records(source.read(logger, conf, catalog, state), "deletions_test")
    assert documents == []

    source.client.query(q.delete(ref(102, "deletions_test")))

    print("=== check: make sure another deleted document produces one more record")
    documents, state = read_records(source.read(logger, conf, catalog, state), "deletions_test")
    assert len(documents) == 1

    assert documents[0]["ref"] == "102"
    assert documents[0]["ts"] > db_data[1]["ts"]
    assert "data" not in documents[0]
    assert datetime.fromisoformat(documents[0]["deleted_at"]).timestamp() * 1_000_000 > db_data[1]["ts"]

    print("=== check: make sure we don't produce more deleted documents when nothing changed")
    documents, state = read_records(source.read(logger, conf, catalog, state), "deletions_test")
    assert documents == []


def handle_check(result: AirbyteConnectionStatus):
    if result.status == Status.FAILED:
        print("======================")
        print("CHECK FAILED:", result.message)
        print("======================")
        raise ValueError("check failed")


def read_records(generator, collection_name):
    state = None
    records = []
    for message in generator:
        if message.type == Type.RECORD:
            assert message.record.stream == collection_name
            records.append(message.record.data)
        elif message.type == Type.STATE:
            if state is not None:
                raise ValueError("two state messages")
            state = message.state.data
    if state is None:
        raise ValueError("no state message")
    return records, state


def run_updates_test(db_data, source: SourceFauna, logger, catalog: ConfiguredAirbyteCatalog):
    conf = config(
        {
            "port": 9000,
            "collection": {},
        }
    )
    handle_check(source.check(logger, conf))
    state = {}
    print("=== check: make sure we read the initial state")
    documents, state = read_records(source.read(logger, conf, catalog, state=state), "foo")
    assert documents == [
        {
            "ref": db_data["ref"][0].id(),
            "ts": db_data["ts"][0],
            "data": {"a": 5},
            "ttl": None,
        },
        {
            "ref": db_data["ref"][1].id(),
            "ts": db_data["ts"][1],
            "data": {"a": 6},
            "ttl": None,
        },
        {
            "ref": db_data["ref"][2].id(),
            "ts": db_data["ts"][2],
            "data": {"a": 7},
            "ttl": None,
        },
        {
            "ref": db_data["ref"][3].id(),
            "ts": db_data["ts"][3],
            "data": {"a": 8},
            "ttl": None,
        },
    ]
    print("=== check: make sure the state resumes")
    documents, state = read_records(source.read(logger, conf, catalog, state=state), "foo")
    assert documents == []

    print("=== check: make sure that updates are actually read")
    update_result = source.client.query(
        q.update(
            db_data["ref"][1],
            {
                "data": {"a": 10},
            },
        )
    )
    create_result = source.client.query(
        q.create(
            ref(200, "foo"),
            {
                "data": {"a": 10000},
            },
        )
    )
    documents, state = read_records(source.read(logger, conf, catalog, state=state), "foo")
    assert documents == [
        {
            # Same ref
            "ref": db_data["ref"][1].id(),
            # New ts
            "ts": update_result["ts"],
            # New data
            "data": {"a": 10},
            # Same ttl
            "ttl": None,
        },
        {
            # New ref
            "ref": "200",
            # New ts
            "ts": create_result["ts"],
            # New data
            "data": {"a": 10000},
            # Same ttl
            "ttl": None,
        },
    ]


def run_test(db_data, source: SourceFauna):
    logger = mock_logger()
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="foo", json_schema={}, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
    )
    run_add_removes_test(source, logger, stream)
    run_removes_order_test(source, logger, stream)
    catalog = ConfiguredAirbyteCatalog(streams=[stream])
    run_updates_test(db_data, source, logger, catalog)
    run_general_remove_test(source, logger)


def test_incremental_reads():
    container, db_data, source = setup_container()

    try:
        run_test(db_data, source)
    except Exception as e:
        print(f"ERROR IN TEST: {e}")
        stop_container(container)
        raise
    stop_container(container)
