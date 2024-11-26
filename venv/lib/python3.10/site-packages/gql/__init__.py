"""The primary :mod:`gql` package includes everything you need to
execute GraphQL requests, with the exception of the transports
which are optional:

 - the :func:`gql <gql.gql>` method to parse a GraphQL query
 - the :class:`Client <gql.Client>` class as the entrypoint to execute requests
   and create sessions
"""

from .__version__ import __version__
from .client import Client
from .gql import gql
from .graphql_request import GraphQLRequest

__all__ = [
    "__version__",
    "gql",
    "Client",
    "GraphQLRequest",
]
