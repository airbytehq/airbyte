from inspect import isawaitable
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Dict,
    Optional,
    Union,
)

from ..error import GraphQLError, located_error
from ..execution.collect_fields import collect_fields
from ..execution.execute import (
    assert_valid_execution_arguments,
    execute,
    get_field_def,
    ExecutionContext,
    ExecutionResult,
)
from ..execution.values import get_argument_values
from ..language import DocumentNode
from ..pyutils import Path, inspect
from ..type import GraphQLFieldResolver, GraphQLSchema
from .map_async_iterator import MapAsyncIterator

__all__ = ["subscribe", "create_source_event_stream"]


async def subscribe(
    schema: GraphQLSchema,
    document: DocumentNode,
    root_value: Any = None,
    context_value: Any = None,
    variable_values: Optional[Dict[str, Any]] = None,
    operation_name: Optional[str] = None,
    field_resolver: Optional[GraphQLFieldResolver] = None,
    subscribe_field_resolver: Optional[GraphQLFieldResolver] = None,
) -> Union[AsyncIterator[ExecutionResult], ExecutionResult]:
    """Create a GraphQL subscription.

    Implements the "Subscribe" algorithm described in the GraphQL spec.

    Returns a coroutine object which yields either an AsyncIterator (if successful) or
    an ExecutionResult (client error). The coroutine will raise an exception if a server
    error occurs.

    If the client-provided arguments to this function do not result in a compliant
    subscription, a GraphQL Response (ExecutionResult) with descriptive errors and no
    data will be returned.

    If the source stream could not be created due to faulty subscription resolver logic
    or underlying systems, the coroutine object will yield a single ExecutionResult
    containing ``errors`` and no ``data``.

    If the operation succeeded, the coroutine will yield an AsyncIterator, which yields
    a stream of ExecutionResults representing the response stream.
    """
    result_or_stream = await create_source_event_stream(
        schema,
        document,
        root_value,
        context_value,
        variable_values,
        operation_name,
        subscribe_field_resolver,
    )
    if isinstance(result_or_stream, ExecutionResult):
        return result_or_stream

    async def map_source_to_response(payload: Any) -> ExecutionResult:
        """Map source to response.

        For each payload yielded from a subscription, map it over the normal GraphQL
        :func:`~graphql.execute` function, with ``payload`` as the ``root_value``.
        This implements the "MapSourceToResponseEvent" algorithm described in the
        GraphQL specification. The :func:`~graphql.execute` function provides the
        "ExecuteSubscriptionEvent" algorithm, as it is nearly identical to the
        "ExecuteQuery" algorithm, for which :func:`~graphql.execute` is also used.
        """
        result = execute(
            schema,
            document,
            payload,
            context_value,
            variable_values,
            operation_name,
            field_resolver,
        )
        return await result if isawaitable(result) else result

    # Map every source value to a ExecutionResult value as described above.
    return MapAsyncIterator(result_or_stream, map_source_to_response)


async def create_source_event_stream(
    schema: GraphQLSchema,
    document: DocumentNode,
    root_value: Any = None,
    context_value: Any = None,
    variable_values: Optional[Dict[str, Any]] = None,
    operation_name: Optional[str] = None,
    subscribe_field_resolver: Optional[GraphQLFieldResolver] = None,
) -> Union[AsyncIterable[Any], ExecutionResult]:
    """Create source event stream

    Implements the "CreateSourceEventStream" algorithm described in the GraphQL
    specification, resolving the subscription source event stream.

    Returns a coroutine that yields an AsyncIterable.

    If the client-provided arguments to this function do not result in a compliant
    subscription, a GraphQL Response (ExecutionResult) with descriptive errors and no
    data will be returned.

    If the source stream could not be created due to faulty subscription resolver logic
    or underlying systems, the coroutine object will yield a single ExecutionResult
    containing ``errors`` and no ``data``.

    A source event stream represents a sequence of events, each of which triggers a
    GraphQL execution for that event.

    This may be useful when hosting the stateful subscription service in a different
    process or machine than the stateless GraphQL execution engine, or otherwise
    separating these two steps. For more on this, see the "Supporting Subscriptions
    at Scale" information in the GraphQL spec.
    """
    # If arguments are missing or incorrectly typed, this is an internal developer
    # mistake which should throw an early error.
    assert_valid_execution_arguments(schema, document, variable_values)

    # If a valid context cannot be created due to incorrect arguments,
    # a "Response" with only errors is returned.
    context = ExecutionContext.build(
        schema,
        document,
        root_value,
        context_value,
        variable_values,
        operation_name,
        subscribe_field_resolver=subscribe_field_resolver,
    )

    # Return early errors if execution context failed.
    if isinstance(context, list):
        return ExecutionResult(data=None, errors=context)

    try:
        event_stream = await execute_subscription(context)

        # Assert field returned an event stream, otherwise yield an error.
        if not isinstance(event_stream, AsyncIterable):
            raise TypeError(
                "Subscription field must return AsyncIterable."
                f" Received: {inspect(event_stream)}."
            )
        return event_stream

    except GraphQLError as error:
        # Report it as an ExecutionResult, containing only errors and no data.
        return ExecutionResult(data=None, errors=[error])


async def execute_subscription(context: ExecutionContext) -> AsyncIterable[Any]:
    schema = context.schema

    root_type = schema.subscription_type
    if root_type is None:
        raise GraphQLError(
            "Schema is not configured to execute subscription operation.",
            context.operation,
        )

    root_fields = collect_fields(
        schema,
        context.fragments,
        context.variable_values,
        root_type,
        context.operation.selection_set,
    )
    response_name, field_nodes = next(iter(root_fields.items()))
    field_def = get_field_def(schema, root_type, field_nodes[0])

    if not field_def:
        field_name = field_nodes[0].name.value
        raise GraphQLError(
            f"The subscription field '{field_name}' is not defined.", field_nodes
        )

    path = Path(None, response_name, root_type.name)
    info = context.build_resolve_info(field_def, field_nodes, root_type, path)

    # Implements the "ResolveFieldEventStream" algorithm from GraphQL specification.
    # It differs from "ResolveFieldValue" due to providing a different `resolveFn`.

    try:
        # Build a dictionary of arguments from the field.arguments AST, using the
        # variables scope to fulfill any variable references.
        args = get_argument_values(field_def, field_nodes[0], context.variable_values)

        # Call the `subscribe()` resolver or the default resolver to produce an
        # AsyncIterable yielding raw payloads.
        resolve_fn = field_def.subscribe or context.subscribe_field_resolver

        event_stream = resolve_fn(context.root_value, info, **args)
        if context.is_awaitable(event_stream):
            event_stream = await event_stream
        if isinstance(event_stream, Exception):
            raise event_stream

        return event_stream
    except Exception as error:
        raise located_error(error, field_nodes, path.as_list())
