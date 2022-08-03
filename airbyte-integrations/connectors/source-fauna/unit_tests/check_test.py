from unittest.mock import Mock, MagicMock

from faunadb import query as q
from source_fauna import SourceFauna
from faunadb.objects import Ref
from faunadb.errors import FaunaError, Unauthorized

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import Status, AirbyteStream

from test_util import mock_logger, config

def query_hardcoded(expr):
    print(expr)
    if expr == q.now():
        return 0
    elif expr == q.paginate(q.documents(q.collection("foo")), size=1):
        return ["my_data_here"]
    elif expr == q.paginate(q.documents(q.collection("invalid_collection_name")), size=1):
        raise FaunaError("", "")
    # Results for index 'ts'
    elif expr == q.exists(q.index("ts")):
        return True
    elif expr == q.select("source", q.get(q.index("ts"))):
        return Ref("foo", Ref("collections"))
    elif expr == q.select("values", q.get(q.index("ts")), []):
        return [
            { "field": "ts" },
            { "field": "ref" },
        ]
    # Results for index 'invalid_index_name'
    elif expr == q.exists(q.index("invalid_index_name")):
        return False
    # Results for index 'invalid_source_index'
    elif expr == q.exists(q.index("invalid_source_index")):
        return True
    elif expr == q.select("source", q.get(q.index("invalid_source_index"))):
        return Ref("wrong_collection", Ref("collections"))
    # Results for index 'no_values_index'
    elif expr == q.exists(q.index("no_values_index")):
        return True
    elif expr == q.select("source", q.get(q.index("no_values_index"))):
        return Ref("foo", Ref("collections"))
    elif expr == q.select("values", q.get(q.index("no_values_index")), []):
        return []
    # Results for index 'extra_values_index'
    elif expr == q.exists(q.index("extra_values_index")):
        return True
    elif expr == q.select("source", q.get(q.index("extra_values_index"))):
        return Ref("foo", Ref("collections"))
    elif expr == q.select("values", q.get(q.index("extra_values_index")), []):
        return [
            { "field": "ts" },
            { "field": "ref" },
            { "field": "lots" },
            { "field": "of" },
            { "field": "extras" },
        ]
    else:
        raise ValueError(f"invalid query {expr}")

# Asserts that the client is setup, and that the client is used to make sure the database is up.
def test_valid_query():
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.client.query = query_hardcoded

    logger = mock_logger()
    result = source.check(logger, config=config({}))
    print(result)
    assert result.status == Status.SUCCEEDED

    assert source._setup_client.called
    assert not logger.error.called

def test_invalid_check():
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.client.query = query_hardcoded

    request_result = MagicMock()
    request_result.response_content = { "errors": [
        { "code": "403", "description": "Unauthorized" }
    ] }
    source.client.query = Mock(side_effect=Unauthorized(request_result))

    print(source.client)

    logger = mock_logger()
    result = source.check(logger, config=config({
        "secret": "some invalid secret",
    }))
    assert result.status == Status.FAILED
    # We should get an unauthorized when there is a valid database, but an invalid key
    assert result.message == "Failed to connect to database: Unauthorized"

    assert source._setup_client.called
    assert not logger.error.called

def mock_source() -> SourceFauna:
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.client.query = query_hardcoded
    return source

def test_check_fails():
    def expect_fail(conf):
        source = mock_source()
        logger = mock_logger()
        result = source.check(logger, config=config({
            "collection": conf,
        }))
        print(result.message)
        assert result.status == Status.FAILED
    def expect_succeed(conf):
        source = mock_source()
        logger = mock_logger()
        result = source.check(logger, config=config({
            "collection": conf,
        }))
        print(result.message)
        assert result.status == Status.SUCCEEDED

    # Each of these tests relies on the behavior of query_hardcoded, defined at the top of this file.

    # Valid collection "foo"
    expect_succeed({
        "name": "foo",
        "index": "",
    })
    # No collection "invalid_collection_name"
    expect_fail({
        "name": "invalid_collection_name",
        "index": "",
    })
    # Valid index "ts"
    expect_succeed({
        "name": "foo",
        "index": "ts",
    })
    # No index "invalid_index_name"
    expect_fail({
        "name": "foo",
        "index": "invalid_index_name",
    })
    # Wrong source on index "invalid_source"
    expect_fail({
        "name": "foo",
        "index": "wrong_source",
    })
    # Extra values on index "extra_values_index", which is fine
    expect_succeed({
        "name": "foo",
        "index": "extra_values_index",
    })
    # Not enough values on index "no_values_index"
    expect_fail({
        "name": "foo",
        "index": "no_values_index",
    })

def test_config_columns():
    def expect_fail(columns):
        source = mock_source()
        logger = mock_logger()
        result = source.check(logger, config=config({
            "collection": {
                "additional_columns": columns,
            },
        }))
        assert result.status == Status.FAILED
    def expect_succeed(columns):
        source = mock_source()
        logger = mock_logger()
        result = source.check(logger, config=config({
            "collection": {
                "additional_columns": columns,
            },
        }))
        assert result.status == Status.SUCCEEDED

    # Invalid column name "data"
    expect_fail([{
        "name": "data",
        "path": ["data"],
        "type": "object",
        "required": True,
    }])
    # Invalid column name "ref"
    expect_fail([{
        "name": "ref",
        "path": ["data"],
        "type": "object",
        "required": True,
    }])
    # Invalid column name "ts"
    expect_fail([{
        "name": "ts",
        "path": ["data"],
        "type": "object",
        "required": True,
    }])
    # Valid column name "my_column"
    expect_succeed([{
        "name": "my_column",
        "path": ["data"],
        "type": "object",
        "required": True,
    }])

    # No duplicate columns
    expect_fail([
        {
            "name": "duplicate_name",
            "path": ["data"],
            "type": "object",
            "required": True,
        },
        {
            "name": "duplicate_name",
            "path": ["data"],
            "type": "object",
            "required": True,
        },
    ])
    # Valid config
    expect_succeed([
        {
            "name": "column_1",
            "path": ["data"],
            "type": "object",
            "required": True,
        },
        {
            "name": "column_2",
            "path": ["data"],
            "type": "object",
            "required": True,
        },
    ])
