from __future__ import annotations

from graphql import DocumentNode, Source, parse


def gql(request_string: str | Source) -> DocumentNode:
    """Given a string containing a GraphQL request, parse it into a Document.

    :param request_string: the GraphQL request as a String
    :type request_string: str | Source
    :return: a Document which can be later executed or subscribed by a
        :class:`Client <gql.client.Client>`, by an
        :class:`async session <gql.client.AsyncClientSession>` or by a
        :class:`sync session <gql.client.SyncClientSession>`

    :raises GraphQLError: if a syntax error is encountered.
    """
    if isinstance(request_string, Source):
        source = request_string
    elif isinstance(request_string, str):
        source = Source(request_string, "GraphQL request")
    else:
        raise TypeError("Request must be passed as a string or Source object.")
    return parse(source)
