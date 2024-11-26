import abc
from typing import Any, AsyncGenerator, Dict, Optional

from graphql import DocumentNode, ExecutionResult


class AsyncTransport(abc.ABC):
    @abc.abstractmethod
    async def connect(self):
        """Coroutine used to create a connection to the specified address"""
        raise NotImplementedError(
            "Any AsyncTransport subclass must implement connect method"
        )  # pragma: no cover

    @abc.abstractmethod
    async def close(self):
        """Coroutine used to Close an established connection"""
        raise NotImplementedError(
            "Any AsyncTransport subclass must implement close method"
        )  # pragma: no cover

    @abc.abstractmethod
    async def execute(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute the provided document AST for either a remote or local GraphQL
        Schema."""
        raise NotImplementedError(
            "Any AsyncTransport subclass must implement execute method"
        )  # pragma: no cover

    @abc.abstractmethod
    def subscribe(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """Send a query and receive the results using an async generator

        The query can be a graphql query, mutation or subscription

        The results are sent as an ExecutionResult object
        """
        raise NotImplementedError(
            "Any AsyncTransport subclass must implement subscribe method"
        )  # pragma: no cover
