#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock

from faunadb import query as q
from faunadb.errors import Unauthorized
from faunadb.objects import Ref
from source_fauna import SourceFauna
from test_util import config, mock_logger

from airbyte_cdk.models import Status


def query_hardcoded(expr):
    print(expr)
    if expr == q.now():
        return 0
    elif expr == q.paginate(q.collections()):
        return [{"ref": Ref("foo", Ref("collections"))}]
    elif expr == q.paginate(q.indexes()):
        return [
            {
                "source": Ref("foo", Ref("collections")),
                "values": [
                    {"field": "ts"},
                    {"field": "ref"},
                ],
                "terms": [],
            }
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
    request_result.response_content = {"errors": [{"code": "403", "description": "Unauthorized"}]}
    source.client.query = Mock(side_effect=Unauthorized(request_result))

    print(source.client)

    logger = mock_logger()
    result = source.check(
        logger,
        config=config(
            {
                "secret": "some invalid secret",
            }
        ),
    )
    assert result.status == Status.FAILED
    # We should get an unauthorized when there is a valid database, but an invalid key
    assert result.message == "Failed to connect to database: Unauthorized"

    assert source._setup_client.called
    assert not logger.error.called
