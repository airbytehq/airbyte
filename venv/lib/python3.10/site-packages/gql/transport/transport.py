import abc
from typing import List

from graphql import DocumentNode, ExecutionResult

from ..graphql_request import GraphQLRequest


class Transport(abc.ABC):
    @abc.abstractmethod
    def execute(self, document: DocumentNode, *args, **kwargs) -> ExecutionResult:
        """Execute GraphQL query.

        Execute the provided document AST for either a remote or local GraphQL Schema.

        :param document: GraphQL query as AST Node or Document object.
        :return: ExecutionResult
        """
        raise NotImplementedError(
            "Any Transport subclass must implement execute method"
        )  # pragma: no cover

    def execute_batch(
        self,
        reqs: List[GraphQLRequest],
        *args,
        **kwargs,
    ) -> List[ExecutionResult]:
        """Execute multiple GraphQL requests in a batch.

        Execute the provided requests for either a remote or local GraphQL Schema.

        :param reqs: GraphQL requests as a list of GraphQLRequest objects.
        :return: a list of ExecutionResult objects
        """
        raise NotImplementedError(
            "This Transport has not implemented the execute_batch method"
        )  # pragma: no cover

    def connect(self):
        """Establish a session with the transport."""
        pass  # pragma: no cover

    def close(self):
        """Close the transport

        This method doesn't have to be implemented unless the transport would benefit
        from it. This is currently used by the RequestsHTTPTransport transport to close
        the session's connection pool.
        """
        pass  # pragma: no cover
