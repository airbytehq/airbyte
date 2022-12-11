#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

from faunadb import query as q
from faunadb.objects import Ref


def ref(id: int, collection="foo") -> Ref:
    return Ref(str(id), cls=Ref(collection, cls=Ref("collections")))


def mock_logger():
    def mock_log(level: str):
        def perform_mock_log(msg: str):
            print(f"[{level}]: {msg}")

        return Mock(side_effect=perform_mock_log)

    logger = Mock()
    logger.info = mock_log("info")
    logger.error = mock_log("error")
    return logger


class DeletionsConfig:
    def __init__(self, mode: str, column=""):
        self.mode = mode
        self.column = column

    @staticmethod
    def ignore() -> "DeletionsConfig":
        return DeletionsConfig(mode="ignore")

    @staticmethod
    def deleted_field(column: str) -> "DeletionsConfig":
        return DeletionsConfig(mode="deleted_field", column=column)


class CollectionConfig:
    def __init__(
        self,
        page_size=64,
        deletions=DeletionsConfig.ignore(),
    ):
        self.page_size = page_size
        self.deletions = deletions


class DiscoverConfig:
    """
    A limited version of FullConfig, storing only the values needed for discover()
    """

    def __init__(self, collection: CollectionConfig):
        self.collection = collection


class FullConfig:
    def __init__(self, domain: str, port: int, scheme: str, secret: str, collection=CollectionConfig()):
        self.domain = domain
        self.port = port
        self.scheme = scheme
        self.secret = secret
        self.collection = collection

    @staticmethod
    def localhost(collection=CollectionConfig()) -> "FullConfig":
        # 9000 is our testing db, that we spawn in database_test.py
        return FullConfig(domain="127.0.0.1", port=9000, scheme="http", secret="secret", collection=collection)


def partial_overwrite(obj: dict, new: dict) -> dict:
    """
    Recursively replaces the values in obj with the values in new.
    """
    for k, v in new.items():
        if type(v) is dict:
            partial_overwrite(obj[k], v)
        else:
            obj[k] = v
    return obj


def config(extra: dict[str, any]) -> dict[str, any]:
    obj = {
        "domain": "127.0.0.1",
        "port": 8443,
        "scheme": "http",
        "secret": "secret",
        "collection": {
            "page_size": 64,
            "deletions": {"deletion_mode": "ignore"},
        },
    }
    return partial_overwrite(obj, extra)


def expand_columns_query(ref):
    doc = q.var("document")
    return q.let(
        {
            "document": q.get(ref),
        },
        {
            "ref": q.select(["ref", "id"], doc),
            "ts": q.select("ts", doc),
            "data": q.select("data", doc, {}),
            "ttl": q.select("ttl", doc, None),
        },
    )
