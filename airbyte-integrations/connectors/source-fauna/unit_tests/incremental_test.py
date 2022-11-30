#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from typing import Dict, Generator
from unittest.mock import MagicMock, Mock

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from faunadb import _json
from faunadb import query as q
from source_fauna import SourceFauna
from test_util import CollectionConfig, config, expand_columns_query, mock_logger, ref

NOW = 1234512987


def results(modified, after):
    modified_obj = {"data": modified}
    if after is not None:
        modified_obj["after"] = after
    return modified_obj


def record(stream: str, data: dict[str, any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            data=data,
            stream=stream,
            emitted_at=NOW,
        ),
    )


def state(data: dict[str, any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            data=data,
            emitted_at=NOW,
        ),
    )


# Tests to make sure the read() function handles the various config combinations of
# updates/deletions correctly.
def test_read_no_updates_or_creates_but_removes_present():
    def find_index_for_stream(collection: str) -> str:
        return "ts"

    def read_updates_hardcoded(
        logger, stream: ConfiguredAirbyteStream, conf: CollectionConfig, state: Dict[str, any], index: str, page_size: int
    ) -> Generator[any, None, None]:
        return []

    def read_removes_hardcoded(
        logger,
        stream: ConfiguredAirbyteStream,
        conf,
        state,
        deletion_column: str,
    ) -> Generator[any, None, None]:
        yield {
            "ref": "555",
            "ts": 5,
            "my_deleted_column": 5,
        }
        yield {
            "ref": "123",
            "ts": 3,
            "my_deleted_column": 3,
        }

    source = SourceFauna()
    source._setup_client = Mock()
    source.read_all = Mock()
    source.find_index_for_stream = find_index_for_stream
    source.read_updates = read_updates_hardcoded
    source.read_removes = read_removes_hardcoded
    source.client = MagicMock()
    source.find_emitted_at = Mock(return_value=NOW)

    logger = mock_logger()
    # Simplest query. Here we should only query Events(), and only track adds.
    result = list(
        source.read(
            logger,
            config(
                {
                    "collection": {
                        "name": "my_stream_name",
                        "deletions": {
                            "deletion_mode": "deleted_field",
                            "column": "my_deleted_column",
                        },
                    }
                }
            ),
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.append_dedup,
                        stream=AirbyteStream(
                            name="my_stream_name",
                            json_schema={},
                            supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                        ),
                    )
                ]
            ),
            state={},
        )
    )
    # read_removes should update the state, so we should see a state message in the output.
    assert result == [
        record(
            "my_stream_name",
            {
                "ref": "555",
                "ts": 5,
                "my_deleted_column": 5,
            },
        ),
        record(
            "my_stream_name",
            {
                "ref": "123",
                "ts": 3,
                "my_deleted_column": 3,
            },
        ),
        state(
            {
                "my_stream_name": {
                    "remove_cursor": {},
                    "updates_cursor": {},
                }
            }
        ),
    ]

    assert source._setup_client.called
    assert not source.read_all.called
    assert not logger.error.called


# Test to make sure read() calls read_updates() correctly.
def test_read_updates_ignore_deletes():
    was_called = False

    def find_index_for_stream(collection: str) -> str:
        return "my_stream_name_ts"

    def read_updates_hardcoded(
        logger, stream: ConfiguredAirbyteStream, conf, state: dict[str, any], index: str, page_size: int
    ) -> Generator[any, None, None]:
        yield {
            "some_document": "data_here",
            "ts": 5,
        }
        yield {
            "more_document": "data_here",
            "ts": 3,
        }

    def read_removes_hardcoded(
        logger,
        stream: ConfiguredAirbyteStream,
        conf,
        state,
        deletion_column: str,
    ) -> Generator[any, None, None]:
        nonlocal was_called
        was_called = True
        yield {
            "ref": "555",
            "ts": 5,
            "my_deleted_column": 5,
        }
        yield {
            "ref": "123",
            "ts": 3,
            "my_deleted_column": 3,
        }

    source = SourceFauna()
    source._setup_client = Mock()
    source.read_all = Mock()
    source.find_index_for_stream = find_index_for_stream
    source.read_updates = read_updates_hardcoded
    source.read_removes = read_removes_hardcoded
    source.client = MagicMock()
    source.find_emitted_at = Mock(return_value=NOW)

    logger = mock_logger()
    # Here we want updates and adds (no deletions), so Events() should be skipped.
    result = list(
        source.read(
            logger,
            config(
                {
                    "collection": {
                        "name": "my_stream_name",
                        "deletions": {
                            "deletion_mode": "ignore",
                        },
                    }
                }
            ),
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.append_dedup,
                        stream=AirbyteStream(
                            name="my_stream_name",
                            json_schema={},
                            supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                        ),
                    )
                ]
            ),
            state={},
        )
    )
    # Here we also validate that the cursor will stay on the latest 'ts' value.
    assert result == [
        record(
            "my_stream_name",
            {
                "some_document": "data_here",
                "ts": 5,
            },
        ),
        record(
            "my_stream_name",
            {
                "more_document": "data_here",
                "ts": 3,
            },
        ),
        state(
            {
                "my_stream_name": {
                    "updates_cursor": {},
                }
            }
        ),
    ]

    assert source._setup_client.called
    assert not was_called
    assert not source.read_all.called
    assert not logger.error.called


# After a failure, the source should emit the state, which we should pass back in,
# and then it should resume correctly.
def test_read_removes_resume_from_partial_failure():
    PAGE_SIZE = 12344315
    FIRST_AFTER_TOKEN = ["some magical", 3, "data"]
    SECOND_AFTER_TOKEN = ["even more magical", 3, "data"]

    def make_query(after):
        return q.map_(
            q.lambda_(
                "x",
                {
                    "ref": q.select("document", q.var("x")),
                    "ts": q.select("ts", q.var("x")),
                },
            ),
            q.filter_(
                q.lambda_("x", q.equals(q.select(["action"], q.var("x")), "remove")),
                q.paginate(
                    q.documents(q.collection("foo")),
                    events=True,
                    size=PAGE_SIZE,
                    after=after,
                ),
            ),
        )

    current_query = 0
    QUERIES = [
        make_query(
            after={
                "ts": 0,
                "action": "remove",
            }
        ),
        make_query(after=FIRST_AFTER_TOKEN),
        make_query(after=SECOND_AFTER_TOKEN),
        make_query(after={"ts": 12345, "action": "remove", "resource": q.ref(q.collection("foo"), "3")}),
    ]
    QUERY_RESULTS = [
        results(
            # Newest event
            [
                {
                    "ref": ref(100),
                    "ts": 99,
                }
            ],
            after=FIRST_AFTER_TOKEN,
        ),
        results(
            [
                {
                    "ref": ref(5),
                    "ts": 999,
                }
            ],
            after=SECOND_AFTER_TOKEN,
        ),
        results(
            # Oldest event
            [
                {
                    "ref": ref(3),
                    "ts": 12345,
                }
            ],
            after=None,
        ),
        results(
            # Oldest event
            [
                {
                    "ref": ref(3),
                    "ts": 12345,
                }
            ],
            after=None,
        ),
    ]

    failed_yet = False

    def find_index_for_stream(collection: str) -> str:
        return "foo_ts"

    def query_hardcoded(expr):
        nonlocal current_query
        nonlocal failed_yet
        assert expr == QUERIES[current_query]
        result = QUERY_RESULTS[current_query]
        if current_query == 2 and not failed_yet:
            failed_yet = True
            raise ValueError("something has gone terribly wrong")
        current_query += 1
        return result

    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.find_index_for_stream = find_index_for_stream
    source.client.query = query_hardcoded

    logger = mock_logger()
    stream = Mock()
    stream.stream.name = "foo"
    # ts should be "now", which is whatever we want
    # ref must not be present, as we are not resuming
    state = {}
    config = CollectionConfig(page_size=PAGE_SIZE)
    outputs = []
    try:
        for output in source.read_removes(logger, stream, config, state, deletion_column="deletes_here"):
            outputs.append(output)
    except ValueError:
        # This means we caught the error thrown above
        pass
    # We should get the first 2 documents.
    assert outputs == [
        {
            "ref": "100",
            "ts": 99,
            "deletes_here": datetime.utcfromtimestamp(99 / 1_000_000).isoformat(),
        },
        {
            "ref": "5",
            "ts": 999,
            "deletes_here": datetime.utcfromtimestamp(999 / 1_000_000).isoformat(),
        },
    ]
    # Now we make sure our after token was serialized to json,
    # and that it was stored within the state.
    assert state == {
        "after": _json.to_json(SECOND_AFTER_TOKEN),
    }

    # Pass that state back in to resume.
    result = list(source.read_removes(logger, stream, config, state, deletion_column="deletes_here"))
    # We should only get the remaining document (no duplicates).
    assert result == [
        {
            "ref": "3",
            "ts": 12345,
            "deletes_here": datetime.utcfromtimestamp(12345 / 1_000_000).isoformat(),
        }
    ]
    assert state == {
        "ts": 12345,
        "ref": "3",
    }

    result = list(source.read_removes(logger, stream, config, state, deletion_column="deletes_here"))
    # We should skip the one result as it matches the state
    assert result == []
    assert state == {
        "ts": 12345,
        "ref": "3",
    }

    assert not source._setup_client.called
    assert current_query == 4
    assert failed_yet
    assert not logger.error.called


# Make sure we get deleted events when we need them.
def test_read_remove_deletions():
    DATE = datetime(2022, 4, 3).replace(tzinfo=timezone.utc)
    # This is a timestamp in microseconds sync epoch
    TS = DATE.timestamp() * 1_000_000
    PAGE_SIZE = 12344315

    def make_query(after):
        return q.map_(
            q.lambda_(
                "x",
                {
                    "ref": q.select("document", q.var("x")),
                    "ts": q.select("ts", q.var("x")),
                },
            ),
            q.filter_(
                q.lambda_("x", q.equals(q.select(["action"], q.var("x")), "remove")),
                q.paginate(
                    q.documents(q.collection("foo")),
                    events=True,
                    size=PAGE_SIZE,
                    after=after,
                ),
            ),
        )

    current_query = 0
    QUERIES = [
        make_query(
            after={
                "ts": 0,
                "action": "remove",
            }
        ),
        make_query(after={"ts": TS, "action": "remove", "resource": q.ref(q.collection("foo"), "100")}),
        make_query(after={"ts": TS, "action": "remove", "resource": q.ref(q.collection("foo"), "100")}),
    ]
    QUERY_RESULTS = [
        results(
            [
                {
                    "ref": ref(100),
                    "ts": TS,
                }
            ],
            after=None,
        ),
        results(
            [
                {
                    "ref": ref(100),
                    "ts": TS,
                }
            ],
            after=None,
        ),
        results(
            [
                {
                    "ref": ref(100),
                    "ts": TS,
                },
                {
                    "ref": ref(300),
                    "ts": TS + 1_000_000,
                },
            ],
            after=None,
        ),
    ]

    def find_index_for_stream(collection: str) -> str:
        return "foo_ts"

    def query_hardcoded(expr):
        nonlocal current_query
        assert expr == QUERIES[current_query]
        result = QUERY_RESULTS[current_query]
        current_query += 1
        return result

    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.find_index_for_stream = find_index_for_stream
    source.client.query = query_hardcoded

    logger = mock_logger()
    stream = Mock()
    stream.stream.name = "foo"
    # ts should be "now", which is whatever we want
    # ref must not be present, as we are not resuming
    state = {}
    config = CollectionConfig(page_size=PAGE_SIZE)
    outputs = list(source.read_removes(logger, stream, config, state, deletion_column="my_deleted_column"))
    # We should get the first document
    assert outputs == [
        {
            "ref": "100",
            "ts": TS,
            "my_deleted_column": "2022-04-03T00:00:00",
        },
    ]
    # Now we make sure our after token was serialized to json,
    # and that it was stored within the state.
    assert state == {
        "ts": TS,
        "ref": "100",
    }

    outputs = list(source.read_removes(logger, stream, config, state, deletion_column="my_deleted_column"))
    # We should get the first document again, but not emit it
    assert outputs == []
    # State should be the same
    assert state == {
        "ts": TS,
        "ref": "100",
    }

    outputs = list(source.read_removes(logger, stream, config, state, deletion_column="my_deleted_column"))
    # We should get the first and second document but only emit the second
    assert outputs == [
        {
            "ref": "300",
            "ts": TS + 1_000_000,
            "my_deleted_column": "2022-04-03T00:00:01",
        },
    ]
    # Now we make sure our after token was serialized to json,
    # and that it was stored within the state.
    assert state == {
        "ts": TS + 1_000_000,
        "ref": "300",
    }

    assert not source._setup_client.called
    assert current_query == 3
    assert not logger.error.called


def test_read_updates_query():
    """
    Validates that read_updates() queries the database correctly.
    """

    PAGE_SIZE = 12344315
    INDEX = "my_index_name"
    FIRST_AFTER_TOKEN = ["some magical", 3, "data"]
    SECOND_AFTER_TOKEN = ["even more magical", 3, "data"]
    state = {}

    def make_query(after, start=[0]):
        return q.map_(
            q.lambda_("x", expand_columns_query(q.select(1, q.var("x")))),
            q.paginate(
                q.range(q.match(q.index(INDEX)), start, []),
                after=after,
                size=PAGE_SIZE,
            ),
        )

    current_query = 0
    QUERIES = [
        make_query(after=None),
        make_query(after=FIRST_AFTER_TOKEN),
        make_query(after=SECOND_AFTER_TOKEN),
        make_query(after=None, start=[999, q.ref(q.collection("my_stream_name"), "10")]),
        make_query(after=None, start=[999, q.ref(q.collection("my_stream_name"), "10")]),
    ]
    # These results come from the query, so they will already be transformed
    # into the columns the user expects. Therefore, we aren't testing much
    # more than the query contents here.
    QUERY_RESULTS = [
        results(
            # Oldest value in index
            [
                {
                    "ref": "3",
                    "ts": 99,
                }
            ],
            after=FIRST_AFTER_TOKEN,
        ),
        results(
            [
                {
                    "ref": "5",
                    "ts": 123,
                }
            ],
            after=SECOND_AFTER_TOKEN,
        ),
        results(
            # Newest value in index
            [
                {
                    "ref": "10",
                    "ts": 999,
                }
            ],
            after=None,
        ),
        results(
            # Newest value in index
            [
                {
                    "ref": "10",
                    "ts": 999,
                }
            ],
            after=None,
        ),
        results(
            # Newest value in index
            [
                {
                    "ref": "10",
                    "ts": 999,
                },
                {
                    "ref": "11",
                    "ts": 1000,
                },
            ],
            after=None,
        ),
    ]

    def query_hardcoded(expr):
        nonlocal current_query
        assert expr == QUERIES[current_query]
        result = QUERY_RESULTS[current_query]
        current_query += 1
        return result

    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.find_index_for_stream = Mock()
    source.client.query = query_hardcoded
    source.find_emitted_at = Mock(return_value=NOW)

    logger = mock_logger()
    # Here we want updates and adds (no deletions), so Events() should be skipped.
    result = list(
        source.read_updates(
            logger,
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(
                    name="my_stream_name",
                    json_schema={},
                    supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                ),
            ),
            CollectionConfig(page_size=PAGE_SIZE),
            state=state,
            index=INDEX,
            page_size=PAGE_SIZE,
        )
    )
    # Here we also validate that the cursor will stay on the latest 'ts' value.
    assert result == [
        {
            "ref": "3",
            "ts": 99,
        },
        {
            "ref": "5",
            "ts": 123,
        },
        {
            "ref": "10",
            "ts": 999,
        },
    ]

    assert state == {"ref": "10", "ts": 999}

    # Call again with the emitted state but no new data, we should get no results
    result = list(
        source.read_updates(
            logger,
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(
                    name="my_stream_name",
                    json_schema={},
                    supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                ),
            ),
            CollectionConfig(page_size=PAGE_SIZE),
            state=state,
            index=INDEX,
            page_size=PAGE_SIZE,
        )
    )
    # Here we also validate that the cursor will stay on the latest 'ts' value.
    assert result == []
    assert state == {"ref": "10", "ts": 999}

    # Call again - we should skip the record in the state again but emit the match
    result = list(
        source.read_updates(
            logger,
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(
                    name="my_stream_name",
                    json_schema={},
                    supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                ),
            ),
            CollectionConfig(page_size=PAGE_SIZE),
            state=state,
            index=INDEX,
            page_size=PAGE_SIZE,
        )
    )
    # Here we also validate that the cursor will stay on the latest 'ts' value.
    assert result == [{"ref": "11", "ts": 1000}]
    assert state == {"ref": "11", "ts": 1000}

    assert not source._setup_client.called
    assert not source.find_index_for_stream.called
    assert not logger.error.called
    assert current_query == 5


def test_read_updates_resume():
    """
    Validates that read_updates() queries the database correctly, and resumes
    a failed query correctly.
    """

    PAGE_SIZE = 12344315
    INDEX = "my_index_name"
    FIRST_AFTER_TOKEN = ["some magical", 3, "data"]
    SECOND_AFTER_TOKEN = ["even more magical", 3, "data"]

    def make_query(after):
        return q.map_(
            q.lambda_("x", expand_columns_query(q.select(1, q.var("x")))),
            q.paginate(
                q.range(q.match(q.index(INDEX)), [0], []),
                after=after,
                size=PAGE_SIZE,
            ),
        )

    current_query = 0
    QUERIES = [
        make_query(after=None),
        make_query(after=FIRST_AFTER_TOKEN),
        make_query(after=SECOND_AFTER_TOKEN),
    ]
    # These results come from the query, so they will already be transformed
    # into the columns the user expects. Therefore, we aren't testing much
    # more than the query contents here.
    QUERY_RESULTS = [
        results(
            # Oldest value in index
            [
                {
                    "ref": "3",
                    "ts": 99,
                }
            ],
            after=FIRST_AFTER_TOKEN,
        ),
        results(
            [
                {
                    "ref": "5",
                    "ts": 123,
                }
            ],
            after=SECOND_AFTER_TOKEN,
        ),
        results(
            # Newest value in index
            [
                {
                    "ref": "10",
                    "ts": 999,
                }
            ],
            after=None,
        ),
    ]
    failed_yet = False

    def query_hardcoded(expr):
        nonlocal current_query
        nonlocal failed_yet
        assert expr == QUERIES[current_query]
        result = QUERY_RESULTS[current_query]
        if current_query == 1 and not failed_yet:
            failed_yet = True
            raise ValueError("oh no something went wrong")
        current_query += 1
        return result

    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.find_index_for_stream = Mock()
    source.client.query = query_hardcoded
    source.find_emitted_at = Mock(return_value=NOW)

    state = {}
    logger = mock_logger()
    # Here we want updates and adds (no deletions), so Events() should be skipped.
    result = []
    got_error = False
    try:
        for record in source.read_updates(
            logger,
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(
                    name="my_stream_name",
                    json_schema={},
                    supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                ),
            ),
            CollectionConfig(page_size=PAGE_SIZE),
            state=state,
            index=INDEX,
            page_size=PAGE_SIZE,
        ):
            result.append(record)
    except ValueError:
        got_error = True
    assert "ts" not in state  # This is set after we finish reading
    assert "ref" not in state  # This is set after we finish reading
    assert "after" in state  # This is some after token, serialized to json
    assert got_error
    assert current_query == 1
    # Here we also validate that the cursor will stay on the latest 'ts' value.
    assert result == [
        {
            "ref": "3",
            "ts": 99,
        },
    ]
    assert list(
        source.read_updates(
            logger,
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(
                    name="my_stream_name",
                    json_schema={},
                    supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
                ),
            ),
            CollectionConfig(page_size=PAGE_SIZE),
            state=state,
            index=INDEX,
            page_size=PAGE_SIZE,
        )
    ) == [
        {
            "ref": "5",
            "ts": 123,
        },
        {
            "ref": "10",
            "ts": 999,
        },
    ]

    assert state["ts"] == 999  # This is set after we finish reading
    assert state["ref"] == "10"  # This is set after we finish reading
    assert "after" not in state  # This is some after token, serialized to json
    assert not source._setup_client.called
    assert not source.find_index_for_stream.called
    assert not logger.error.called
    assert current_query == 3
