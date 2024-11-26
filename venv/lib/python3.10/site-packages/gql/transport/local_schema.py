import asyncio
from inspect import isawaitable
from typing import AsyncGenerator, Awaitable, cast

from graphql import DocumentNode, ExecutionResult, GraphQLSchema, execute, subscribe

from gql.transport import AsyncTransport


class LocalSchemaTransport(AsyncTransport):
    """A transport for executing GraphQL queries against a local schema."""

    def __init__(
        self,
        schema: GraphQLSchema,
    ):
        """Initialize the transport with the given local schema.

        :param schema: Local schema as GraphQLSchema object
        """
        self.schema = schema

    async def connect(self):
        """No connection needed on local transport"""
        pass

    async def close(self):
        """No close needed on local transport"""
        pass

    async def execute(
        self,
        document: DocumentNode,
        *args,
        **kwargs,
    ) -> ExecutionResult:
        """Execute the provided document AST for on a local GraphQL Schema."""

        result_or_awaitable = execute(self.schema, document, *args, **kwargs)

        execution_result: ExecutionResult

        if isawaitable(result_or_awaitable):
            result_or_awaitable = cast(Awaitable[ExecutionResult], result_or_awaitable)
            execution_result = await result_or_awaitable
        else:
            result_or_awaitable = cast(ExecutionResult, result_or_awaitable)
            execution_result = result_or_awaitable

        return execution_result

    @staticmethod
    async def _await_if_necessary(obj):
        """This method is necessary to work with
        graphql-core versions < and >= 3.3.0a3"""
        return await obj if asyncio.iscoroutine(obj) else obj

    async def subscribe(
        self,
        document: DocumentNode,
        *args,
        **kwargs,
    ) -> AsyncGenerator[ExecutionResult, None]:
        """Send a subscription and receive the results using an async generator

        The results are sent as an ExecutionResult object
        """

        subscribe_result = await self._await_if_necessary(
            subscribe(self.schema, document, *args, **kwargs)
        )

        if isinstance(subscribe_result, ExecutionResult):
            yield subscribe_result

        else:
            async for result in subscribe_result:
                yield result
